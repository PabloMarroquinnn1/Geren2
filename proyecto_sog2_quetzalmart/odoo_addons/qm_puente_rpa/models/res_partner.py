import re

from odoo import api, fields, models

CAMPOS_TEXTO = ("qm_pais_texto", "qm_estado_texto", "qm_empresa_relacionada", "qm_etiquetas_texto",
                "qm_sitio_web")


class ResPartner(models.Model):
    _inherit = "res.partner"

    # El robot envía estos datos como texto; Odoo los convierte en relaciones al
    # guardar. Así un país, estado o etiqueta escrito de otra forma en el Excel
    # no detiene la importación completa.
    qm_origen_rpa = fields.Char(
        string="Archivo de origen (RPA)", copy=False,
        help="Ruta del Excel desde el que el robot cargó este contacto.")
    qm_pais_texto = fields.Char(string="País (texto RPA)", copy=False)
    qm_estado_texto = fields.Char(string="Estado (texto RPA)", copy=False)
    qm_empresa_relacionada = fields.Char(string="Empresa relacionada (texto RPA)", copy=False)
    qm_etiquetas_texto = fields.Char(string="Etiquetas (texto RPA)", copy=False)
    # La columna "website" se confunde con el campo website_id (sitio de la
    # tienda) en el asistente de importación; por eso viaja por este campo.
    qm_sitio_web = fields.Char(string="Sitio web (texto RPA)", copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        contactos = super().create(vals_list)
        contactos._qm_resolver_textos_rpa()
        return contactos

    def write(self, vals):
        resultado = super().write(vals)
        if not self.env.context.get("qm_resolviendo_rpa") and any(c in vals for c in CAMPOS_TEXTO):
            self._qm_resolver_textos_rpa()
        return resultado

    def _qm_resolver_textos_rpa(self):
        for contacto in self.filtered(lambda c: any(c[campo] for campo in CAMPOS_TEXTO)):
            valores = {}
            pais = self._qm_buscar_pais(contacto.qm_pais_texto)
            if pais:
                valores["country_id"] = pais.id
            estado = self._qm_buscar_estado(contacto.qm_estado_texto, pais or contacto.country_id)
            if estado:
                valores["state_id"] = estado.id
                valores.setdefault("country_id", estado.country_id.id)
            if contacto.qm_empresa_relacionada:
                empresa = self._qm_empresa(contacto.qm_empresa_relacionada, valores.get("country_id"))
                if empresa != contacto:
                    valores["parent_id"] = empresa.id
            if contacto.qm_sitio_web:
                valores["website"] = contacto.qm_sitio_web
            if contacto.qm_etiquetas_texto:
                etiquetas = self._qm_etiquetas(contacto.qm_etiquetas_texto)
                valores["category_id"] = [fields.Command.link(e.id) for e in etiquetas]
            if valores:
                contacto.with_context(qm_resolviendo_rpa=True).write(valores)

    @api.model
    def _qm_buscar_pais(self, texto):
        texto = (texto or "").strip()
        if not texto:
            return self.env["res.country"]
        Pais = self.env["res.country"]
        if len(texto) == 2:
            pais = Pais.search([("code", "=ilike", texto)], limit=1)
            if pais:
                return pais
        for idioma in ("es_419", "en_US"):
            pais = Pais.with_context(lang=idioma).search([("name", "=ilike", texto)], limit=1)
            if pais:
                return pais
        return Pais.search([("name", "ilike", texto)], limit=1)

    @api.model
    def _qm_buscar_estado(self, texto, pais):
        texto = (texto or "").strip()
        if not texto:
            return self.env["res.country.state"]
        dominio = [("country_id", "=", pais.id)] if pais else []
        Estado = self.env["res.country.state"]
        return (Estado.search(dominio + [("code", "=ilike", texto)], limit=1)
                or Estado.search(dominio + [("name", "=ilike", texto)], limit=1))

    @api.model
    def _qm_empresa(self, nombre, pais_id):
        nombre = nombre.strip()
        empresa = self.search([("name", "=ilike", nombre), ("is_company", "=", True)], limit=1)
        if not empresa:
            empresa = self.create({"name": nombre, "is_company": True, "country_id": pais_id})
        return empresa

    @api.model
    def _qm_etiquetas(self, texto):
        Etiqueta = self.env["res.partner.category"]
        etiquetas = Etiqueta
        for nombre in filter(None, (n.strip() for n in re.split(r"[,;]", texto))):
            etiquetas |= Etiqueta.search([("name", "=ilike", nombre)], limit=1) or Etiqueta.create({"name": nombre})
        return etiquetas
