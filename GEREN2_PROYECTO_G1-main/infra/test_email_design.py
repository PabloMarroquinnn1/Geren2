"""Send two internal design previews to a synthetic Mailpit-only address."""

recipient = "prueba.diseno.20261002@quetzalmart.local"
invoice = env["account.move"].search([("name", "=", "INV/2026/00165")], limit=1)
assert invoice
template = env.ref("account.email_template_edi_invoice").with_context(lang="es_419")
invoice_mail_id = template.send_mail(
    invoice.id,
    force_send=True,
    email_values={"email_to": recipient, "auto_delete": False},
)
invoice_mail = env["mail.mail"].browse(invoice_mail_id)
assert invoice_mail.state == "sent", invoice_mail.state

mailing = env["mailing.mailing"].search(
    [("subject", "=", "QuetzalMart | Beneficios de temporada y compra segura"),
     ("state", "=", "done")], order="id desc", limit=1
)
campaign_mail = env["mail.mail"].sudo().create({
    "subject": mailing.subject,
    "body_html": mailing.body_html,
    "email_from": mailing.email_from,
    "email_to": recipient,
    "auto_delete": False,
})
campaign_mail.send(raise_exception=True)
assert campaign_mail.state == "sent", campaign_mail.state
env.cr.commit()
print("PREVIEW_RECIPIENT", recipient)
print("INVOICE_MAIL", invoice_mail_id, invoice_mail.state)
print("CAMPAIGN_MAIL", campaign_mail.id, campaign_mail.state)
