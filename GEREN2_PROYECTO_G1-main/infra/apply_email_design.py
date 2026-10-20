"""Install the branded invoice and campaign designs in the live Odoo database."""

import base64
from pathlib import Path


base = Path("/tmp/qm-email-design")
website = "https://quetzalmart.34-9-149-41.sslip.io"
hero = (base / "beneficios-temporada-hero.jpg").read_bytes()
assert hero.startswith(b"\xff\xd8\xff"), "The campaign image is not a JPEG"

attachment = env["ir.attachment"].sudo().search(
    [("name", "=", "beneficios-temporada-hero.jpg"), ("public", "=", True)], limit=1
)
values = {
    "name": "beneficios-temporada-hero.jpg",
    "type": "binary",
    "datas": base64.b64encode(hero),
    "mimetype": "image/jpeg",
    "public": True,
}
if attachment:
    attachment.write(values)
else:
    attachment = env["ir.attachment"].sudo().create(values)
hero_url = f"{website}/web/content/{attachment.id}?download=false"

campaign_body = (base / "campaign_beneficios.html").read_text(encoding="utf-8")
assert campaign_body.count("__HERO_URL__") == 1
campaign_body = campaign_body.replace("__HERO_URL__", hero_url)
mailing = env["mailing.mailing"].sudo().search(
    [("subject", "=", "QuetzalMart | Beneficios de temporada y compra segura"),
     ("state", "=", "done")], order="id desc", limit=1
)
assert mailing, "The campaign used by the post-purchase automation was not found"
mailing.write({"body_html": campaign_body})
assert hero_url in str(mailing.body_html)

invoice_body = (base / "invoice_es419.html").read_text(encoding="utf-8")
template = env.ref("account.email_template_edi_invoice").with_context(lang="es_419")
template.write({"body_html": invoice_body})
invoice = env["account.move"].search([("name", "=", "INV/2026/00165")], limit=1)
assert invoice, "The sample invoice for rendering was not found"
rendered = template._render_field("body_html", [invoice.id])[invoice.id]
for expected in (invoice.name, invoice.invoice_origin, invoice.partner_id.name):
    assert expected in rendered, ("Missing invoice field in rendered email", expected)
assert "INV/2026/00153" not in rendered

env.cr.commit()
print("Campaign mailing", mailing.id, "updated; hero attachment", attachment.id)
print("Invoice template rendered with", invoice.name, invoice.invoice_origin)
print("HERO_URL", hero_url)
