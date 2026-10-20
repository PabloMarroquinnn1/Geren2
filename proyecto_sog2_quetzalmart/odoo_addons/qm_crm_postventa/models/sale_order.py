import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)

# Segundos entre el correo de la factura y el de la campaña: así el cliente
# siempre recibe primero la compra y después el marketing.
ESPERA_CAMPANA = 45


class SaleOrder(models.Model):
    _inherit = "sale.order"

    qm_campana_enviada = fields.Datetime(
        string="Campaña postcompra programada", copy=False, readonly=True)

    def action_confirm(self):
        resultado = super().action_confirm()
        for pedido in self.sudo().filtered(lambda p: p.website_id and p.state == "sale"):
            try:
                with self.env.cr.savepoint():
                    pedido._qm_registrar_en_crm()
            except Exception:
                # Un problema del CRM no debe revertir la compra del cliente.
                _logger.exception("No se pudo registrar en el CRM el pedido %s", pedido.name)
        return resultado

    def _qm_registrar_en_crm(self):
        """Convierte el registro web del cliente (o crea una oportunidad) y la marca ganada."""
        self.ensure_one()
        if self.opportunity_id:
            return self.opportunity_id
        Lead = self.env["crm.lead"].sudo()
        cliente = self.partner_id.commercial_partner_id
        oportunidad = Lead.search([
            ("partner_id", "child_of", cliente.id),
            ("active", "=", True),
            ("probability", "<", 100),
            ("tag_ids", "in", self.env.ref("qm_crm_postventa.etiqueta_registro_web").ids),
        ], order="id desc", limit=1)
        valores = {
            "name": "Compra en línea %s - %s" % (self.name, self.partner_id.name),
            "type": "opportunity",
            "partner_id": self.partner_id.id,
            "email_from": self.partner_id.email,
            "phone": self.partner_id.phone,
            "expected_revenue": self.amount_untaxed,
            "team_id": (self.team_id or self.website_id.salesteam_id).id,
            "source_id": self.source_id.id or self.env.ref("qm_crm_postventa.origen_tienda").id,
            "medium_id": self.medium_id.id or self.env.ref("utm.utm_medium_website").id,
            "campaign_id": self.campaign_id.id,
            "tag_ids": [fields.Command.link(self.env.ref("qm_crm_postventa.etiqueta_cliente_web").id)],
        }
        if oportunidad:
            oportunidad.write(valores)
        else:
            oportunidad = Lead.create(valores)
        oportunidad.action_set_won()
        self.opportunity_id = oportunidad
        self._qm_suscribir(self.env.ref("qm_crm_postventa.lista_clientes_web"))
        return oportunidad

    def _qm_suscribir(self, lista):
        email = (self.partner_id.email or "").strip().lower()
        if not email:
            return
        Contacto = self.env["mailing.contact"].sudo()
        contacto = Contacto.search([("email", "=ilike", email)], limit=1)
        if contacto:
            contacto.list_ids = [fields.Command.link(lista.id)]
        else:
            Contacto.create({
                "name": self.partner_id.name,
                "email": email,
                "country_id": self.partner_id.country_id.id,
                "list_ids": [fields.Command.link(lista.id)],
            })

    def _qm_programar_campana(self):
        """Pone en cola el correo de marketing, una sola vez por pedido web."""
        plantilla = self.env.ref("qm_crm_postventa.plantilla_campana_postcompra").sudo()
        envio = fields.Datetime.now() + timedelta(seconds=ESPERA_CAMPANA)
        for pedido in self.sudo().filtered(
                lambda p: p.website_id and not p.qm_campana_enviada and p.partner_id.email):
            plantilla.send_mail(pedido.id, email_values={"scheduled_date": envio})
            pedido.qm_campana_enviada = fields.Datetime.now()
            pedido.message_post(body="Campaña postcompra programada para %s." % pedido.partner_id.email)
        self.env.ref("mail.ir_cron_mail_scheduler_action").sudo()._trigger(at=envio)

    def qm_recomendaciones(self, limite=3):
        """Productos publicados que el cliente no compró, de sus mismas categorías primero."""
        self.ensure_one()
        Producto = self.env["product.template"].sudo()
        comprados = self.order_line.product_id.product_tmpl_id
        base = [("is_published", "=", True), ("sale_ok", "=", True), ("id", "not in", comprados.ids)]
        similares = Producto.search(
            base + [("public_categ_ids", "in", comprados.public_categ_ids.ids)],
            order="list_price desc", limit=limite)
        if len(similares) < limite:
            similares |= Producto.search(
                base + [("id", "not in", similares.ids)], order="list_price desc",
                limit=limite - len(similares))
        return similares
