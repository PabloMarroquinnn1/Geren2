"""Check the final demo order without changing it."""

order = env["sale.order"].search([("name", "=", "S00188")], limit=1)
print("ORDER", order.name, order.state, "PAID", order.amount_total)
print("PARTNER", order.partner_id.email)
print("CAMPAIGN_SENT", bool(order.qm_campaign_sent_at))
for invoice in order.invoice_ids:
    print("INVOICE", invoice.name, invoice.state, invoice.amount_total)
