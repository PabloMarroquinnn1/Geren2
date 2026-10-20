company = env.company
country_gt = env.ref("base.gt")
currency_gtq = env.ref("base.GTQ")

for currency_code in ("GTQ", "USD", "MXN"):
    currency = env["res.currency"].search([("name", "=", currency_code)], limit=1)
    if currency:
        currency.active = True

company.write({
    "name": "QuetzalMart",
    "country_id": country_gt.id,
    "currency_id": currency_gtq.id,
    "email": "info@quetzalmart.local",
    "phone": "+502 2200 2026",
})
company.partner_id.write({
    "name": "QuetzalMart",
    "country_id": country_gt.id,
    "city": "Ciudad de Guatemala",
    "street": "Zona 10",
    "email": "info@quetzalmart.local",
    "phone": "+502 2200 2026",
})

language = env["res.lang"].search([("code", "=", "es_419")], limit=1)
if language and not language.active:
    env["res.lang"]._activate_lang("es_419")

admin = env.ref("base.user_admin")
admin_values = {"tz": "America/Guatemala"}
if language:
    admin_values["lang"] = "es_419"
admin.write(admin_values)

env["ir.config_parameter"].sudo().set_param(
    "web.base.url", "https://quetzalmart.34-9-149-41.sslip.io"
)
env["ir.config_parameter"].sudo().set_param("web.base.url.freeze", "True")
env.cr.commit()

