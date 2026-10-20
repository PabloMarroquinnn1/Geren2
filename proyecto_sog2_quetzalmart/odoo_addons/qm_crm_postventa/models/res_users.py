import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _signup_create_user(self, values):
        usuario = super()._signup_create_user(values)
        try:
            with self.env.cr.savepoint():
                usuario.sudo()._qm_registrar_lead_web()
        except Exception:
            _logger.exception("No se pudo crear el lead del registro web de %s", usuario.login)
        return usuario

    def _qm_registrar_lead_web(self):
        """Quien se registra en la tienda entra al CRM como lead y a la lista de correo."""
        socio = self.partner_id
        website = self.env["website"].get_current_website()
        self.env["crm.lead"].create({
            "name": "Registro en la tienda: %s" % socio.name,
            "type": "lead",
            "partner_id": socio.id,
            "contact_name": socio.name,
            "email_from": socio.email or self.login,
            "team_id": website.salesteam_id.id,
            "source_id": self.env.ref("qm_crm_postventa.origen_tienda").id,
            "medium_id": self.env.ref("utm.utm_medium_website").id,
            "tag_ids": [fields.Command.link(self.env.ref("qm_crm_postventa.etiqueta_registro_web").id)],
            "description": "Cuenta creada desde el sitio web de QuetzalMart.",
        })
        email = (socio.email or self.login or "").strip().lower()
        if "@" in email:
            lista = self.env.ref("qm_crm_postventa.lista_registros_web")
            Contacto = self.env["mailing.contact"]
            contacto = Contacto.search([("email", "=ilike", email)], limit=1)
            if contacto:
                contacto.list_ids = [fields.Command.link(lista.id)]
            else:
                Contacto.create({"name": socio.name, "email": email,
                                 "list_ids": [fields.Command.link(lista.id)]})
