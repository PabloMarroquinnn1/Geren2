import base64
import logging
import re

from odoo import api, fields, models
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)

LOTE_ARCHIVO = 40


class AccountMove(models.Model):
    _inherit = "account.move"

    qm_documento_id = fields.Many2one(
        "dms.file", string="PDF en Documentos", copy=False, readonly=True,
        index="btree_not_null",
    )
    qm_archivo_pendiente = fields.Boolean(copy=False, index=True)

    def _post(self, soft=True):
        publicados = super()._post(soft=soft)
        por_archivar = publicados.filtered(lambda move: move._qm_se_archiva())
        if por_archivar:
            # El PDF se genera en segundo plano para no hacer esperar al cliente
            # en el pago web ni a la carga masiva.
            por_archivar.qm_archivo_pendiente = True
            self.env.ref("qm_gestion_documental.cron_archivar_facturas")._trigger()
        return publicados

    def _qm_se_archiva(self):
        self.ensure_one()
        if self.move_type in ("out_invoice", "out_refund"):
            return True
        if self.move_type in ("in_invoice", "in_refund"):
            parametro = self.env["ir.config_parameter"].sudo().get_param(
                "qm_gestion_documental.archivar_facturas_proveedor", "False")
            return str2bool(parametro)
        return False

    @api.model
    def _qm_cron_archivar_facturas(self):
        pendientes = self.search(
            [("qm_archivo_pendiente", "=", True), ("state", "=", "posted")],
            order="id", limit=LOTE_ARCHIVO,
        )
        archivadas = 0
        for factura in pendientes:
            try:
                with self.env.cr.savepoint():
                    factura._qm_archivar_pdf()
                archivadas += 1
            except Exception:
                # Queda pendiente: el cron horario lo vuelve a intentar.
                _logger.exception("No se pudo archivar el PDF de %s", factura.name)
        quedan = self.search_count([("qm_archivo_pendiente", "=", True), ("state", "=", "posted")])
        if archivadas and quedan:
            self.env.ref("qm_gestion_documental.cron_archivar_facturas")._trigger()

    @api.model
    def qm_reintentar_archivo(self):
        """Marca para archivar las facturas publicadas que aún no tienen su PDF en Documentos."""
        faltantes = self.search([("state", "=", "posted"), ("qm_documento_id", "=", False),
                                 ("move_type", "in", ("out_invoice", "out_refund", "in_invoice", "in_refund"))])
        faltantes = faltantes.filtered(lambda move: move._qm_se_archiva())
        faltantes.qm_archivo_pendiente = True
        if faltantes:
            self.env.ref("qm_gestion_documental.cron_archivar_facturas")._trigger()
        return len(faltantes)

    def action_qm_archivar_ahora(self):
        for factura in self.filtered(lambda move: move.state == "posted"):
            factura._qm_archivar_pdf()
        return True

    def action_qm_ver_documento(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "dms.file",
            "res_id": self.qm_documento_id.id,
            "view_mode": "form",
        }

    def _qm_archivar_pdf(self):
        self.ensure_one()
        es_venta = self.move_type in ("out_invoice", "out_refund")
        ref = self.env.ref
        carpeta = ref("qm_gestion_documental.carpeta_facturas_venta" if es_venta
                      else "qm_gestion_documental.carpeta_facturas_proveedor")
        categoria = ref("qm_gestion_documental.categoria_factura_venta" if es_venta
                        else "qm_gestion_documental.categoria_factura_proveedor")
        etiquetas = ref("qm_gestion_documental.etiqueta_erp") | ref(
            "qm_gestion_documental.etiqueta_venta" if es_venta
            else "qm_gestion_documental.etiqueta_proveedor")
        etiquetas |= self._qm_etiqueta(str(self.invoice_date.year if self.invoice_date else
                                          fields.Date.today().year))
        if self.team_id:
            etiquetas |= self._qm_etiqueta(self.team_id.name)
        if self.payment_state in ("paid", "in_payment"):
            etiquetas |= ref("qm_gestion_documental.etiqueta_pagada")

        pdf, _formato = self.env["ir.actions.report"].sudo()._render_qweb_pdf(
            "account.account_invoices", res_ids=self.ids)
        nombre = "%s - %s.pdf" % (self.name, self.partner_id.name or "")
        nombre = re.sub(r'[\\/:*?"<>|]+', "-", nombre).strip()
        valores = {
            "name": nombre,
            "directory_id": carpeta.id,
            "category_id": categoria.id,
            "tag_ids": [fields.Command.set(etiquetas.ids)],
            "content": base64.b64encode(pdf),
            "mimetype": "application/pdf",
        }
        documento = self.qm_documento_id.sudo()
        if documento:
            documento.write(valores)
        else:
            documento = self.env["dms.file"].sudo().create(valores)
        self.write({"qm_documento_id": documento.id, "qm_archivo_pendiente": False})
        _logger.info("Factura %s archivada en Documentos como %s", self.name, nombre)
        return documento

    @api.model
    def _qm_etiqueta(self, nombre):
        Etiqueta = self.env["dms.tag"].sudo()
        return Etiqueta.search([("name", "=", nombre)], limit=1) or Etiqueta.create({"name": nombre})
