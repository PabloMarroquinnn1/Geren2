"""Replace stale demo values in the Spanish invoice email with invoice fields."""

template = env.ref("account.email_template_edi_invoice")
localized = template.with_context(lang="es_419")
body = str(localized.body_html or "")
replacements = {
    "INV/2026/00153": '<t t-out="object.name or \'\'"></t>',
    "S00174": '<t t-out="object.invoice_origin or \'\'"></t>',
    "38,56 Q": '<t t-out="format_amount(object.amount_total, object.currency_id) or \'\'"></t>',
    ">Cliente</strong>": '><t t-out="object.partner_id.name or \'Cliente\'"></t></strong>',
}
for old, new in replacements.items():
    assert body.count(old) == 1, (old, body.count(old))
    body = body.replace(old, new)

localized.write({"body_html": body})
invoice = env["account.move"].search([("name", "=", "INV/2026/00164")], limit=1)
assert invoice, "The invoice used to verify the template was not found"
rendered = localized._render_field("body_html", [invoice.id])[invoice.id]
for expected in (invoice.name, invoice.invoice_origin, invoice.partner_id.name):
    assert expected in rendered, ("Missing rendered invoice field", expected)
for stale in ("INV/2026/00153", "S00174"):
    assert stale not in rendered, ("Stale demo value remains", stale)
env.cr.commit()
print("Updated es_419 invoice email; rendered invoice, sale order, and customer correctly")
