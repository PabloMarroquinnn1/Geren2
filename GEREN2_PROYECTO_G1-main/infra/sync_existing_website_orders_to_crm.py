"""Backfill CRM opportunities for already-confirmed website orders; Odoo shell."""

orders = env["sale.order"].search(
    [
        ("website_id", "!=", False),
        ("state", "in", ["sale", "done"]),
        ("partner_id", "!=", False),
        ("opportunity_id", "=", False),
    ]
)
candidate_count = len(orders)
orders._qm_link_website_orders_to_crm()
env.cr.commit()
linked_count = orders.filtered(lambda order: order.opportunity_id).mapped("id")
print(
    {
        "website_orders_considered": candidate_count,
        "website_orders_linked": len(linked_count),
    }
)
