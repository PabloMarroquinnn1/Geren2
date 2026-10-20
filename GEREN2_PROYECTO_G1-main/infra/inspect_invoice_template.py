"""Inspect the live customer invoice email body without printing its full HTML."""

template = env.ref("account.email_template_edi_invoice")
print("TEMPLATE", template.id, template.name)
needles = ("INV/2026/00153", "S00174", "38,56 Q", "Cliente", "Hola")
for language in ("es_GT", "es_419", "en_US"):
    body = template.with_context(lang=language).body_html or ""
    print("LANG", language, "LENGTH", len(body))
    for needle in needles:
        at = body.find(needle)
        print("NEEDLE", repr(needle), "COUNT", body.count(needle), "AT", at)
        if at >= 0:
            print("CONTEXT", repr(body[max(0, at - 105) : at + len(needle) + 105]))
