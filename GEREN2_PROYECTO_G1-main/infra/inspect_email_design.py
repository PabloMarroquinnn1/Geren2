"""Print only safe metadata for the current QuetzalMart email designs."""

template = env.ref("account.email_template_edi_invoice")
body = str(template.with_context(lang="es_419").body_html or "")
print("INVOICE_TEMPLATE", template.id, "LENGTH", len(body))
print("INVOICE_START", repr(body[:600]))
for mailing in env["mailing.mailing"].search([("subject", "=", "QuetzalMart | Beneficios de temporada y compra segura")], order="id desc", limit=3):
    print("MAILING", mailing.id, mailing.state, "LENGTH", len(mailing.body_html or ""))
    print("MAILING_START", repr(str(mailing.body_html or "")[:650]))
print("COMPANY_LOGO", bool(env.company.logo), "WEBSITE", env["website"].search([], limit=1).domain)
