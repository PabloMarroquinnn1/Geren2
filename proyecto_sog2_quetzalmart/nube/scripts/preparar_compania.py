# Se ejecuta con "odoo shell" justo después de crear la base y ANTES de instalar
# Contabilidad: así Odoo carga el plan de cuentas e impuestos de Guatemala (l10n_gt).
import os

empresa = env.company
guatemala = env.ref("base.gt")
quetzal = env.ref("base.GTQ")
quetzal.active = True

empresa.write({
    "name": "QuetzalMart",
    "country_id": guatemala.id,
    "currency_id": quetzal.id,
})

idioma = env["res.lang"]._activate_lang("es_419")
admin = env.ref("base.user_admin")
admin.write({
    "name": "Administración QuetzalMart",
    "login": os.environ["ODOO_ADMIN_LOGIN"],
    "password": os.environ["ODOO_ADMIN_PASSWORD"],
    "lang": idioma.code,
    "tz": "America/Guatemala",
})
admin.partner_id.email = os.environ["ODOO_ADMIN_LOGIN"]
env.cr.commit()
print("Compañía preparada:", empresa.name, empresa.country_id.code, empresa.currency_id.name)
