from datetime import date, timedelta
from pathlib import Path


company = env.company
products = env["product.product"].search([
    ("default_code", "like", "QM-%"),
], order="default_code")
customers = env["res.partner"].search([
    ("ref", "like", "CLI-%"), ("customer_rank", ">", 0),
], order="ref")
suppliers = env["res.partner"].search([
    ("ref", "like", "PROV-%"), ("supplier_rank", ">", 0),
], order="ref")
warehouses = env["stock.warehouse"].search([
    ("company_id", "=", company.id),
], order="code")

if len(products) < 60 or len(customers) < 30 or len(suppliers) < 25 or len(warehouses) < 3:
    raise RuntimeError("El bloque 4 no contiene todos los datos maestros requeridos.")

# El reporte estándar de factura en es_419 desborda encabezados largos.
# Se usa inglés para los PDF hasta personalizar la plantilla visual en el bloque 6.
report_language = env["res.lang"].search([("code", "=", "en_US")], limit=1)
if report_language:
    customers.write({"lang": report_language.code})
    suppliers.write({"lang": report_language.code})
    company.partner_id.write({"lang": report_language.code})


def sale_lines(seed, count=3):
    commands = []
    for offset in range(count):
        product = products[(seed * 7 + offset * 11) % len(products)]
        commands.append((0, 0, {
            "product_id": product.id,
            "product_uom_qty": 1 + ((seed + offset) % 4),
            "price_unit": product.lst_price,
        }))
    return commands


def purchase_lines(seed, count=3):
    commands = []
    for offset in range(count):
        product = products[(seed * 5 + offset * 13) % len(products)]
        commands.append((0, 0, {
            "product_id": product.id,
            "product_qty": 4 + ((seed + offset) % 7),
            "price_unit": product.standard_price,
            "date_planned": date(2026, 9, 1) + timedelta(days=seed % 18),
        }))
    return commands


def complete_picking(picking):
    if picking.state in ("done", "cancel"):
        return
    picking.action_assign()
    for move in picking.move_ids.filtered(lambda item: item.state not in ("done", "cancel")):
        move.quantity = move.product_uom_qty
    result = picking.button_validate()
    if isinstance(result, dict) and result.get("res_model") == "stock.immediate.transfer":
        wizard = env[result["res_model"]].browse(result["res_id"])
        wizard.process()
    elif isinstance(result, dict) and result.get("res_model") == "stock.backorder.confirmation":
        wizard = env[result["res_model"]].browse(result["res_id"])
        wizard.process()


# Veinte cotizaciones de venta independientes de las 150 ventas.
for index in range(1, 21):
    reference = f"B5-SQ-{index:03d}"
    quotation = env["sale.order"].search([
        ("client_order_ref", "=", reference),
    ], limit=1)
    if not quotation:
        quotation = env["sale.order"].create({
            "partner_id": customers[(index - 1) % len(customers)].id,
            "client_order_ref": reference,
            "warehouse_id": warehouses[(index - 1) % len(warehouses)].id,
            "date_order": date(2026, 8, 1) + timedelta(days=index - 1),
            "note": "Cotización de venta del bloque 5; debe permanecer sin confirmar.",
            "order_line": sale_lines(index, 2),
        })


# Veinte solicitudes de cotización de compra independientes de las 100 compras.
for index in range(1, 21):
    reference = f"B5-PQ-{index:03d}"
    quotation = env["purchase.order"].search([
        ("partner_ref", "=", reference),
    ], limit=1)
    if not quotation:
        quotation = env["purchase.order"].create({
            "partner_id": suppliers[(index - 1) % len(suppliers)].id,
            "partner_ref": reference,
            "date_order": date(2026, 8, 1) + timedelta(days=index - 1),
            "notes": "Cotización de compra del bloque 5; debe permanecer sin confirmar.",
            "order_line": purchase_lines(index, 2),
        })

env.cr.commit()
print("BLOCK5_PROGRESS quotations=40")


# Ciento cincuenta ventas confirmadas y facturadas.
for index in range(1, 151):
    reference = f"B5-SALE-{index:03d}"
    order = env["sale.order"].search([
        ("client_order_ref", "=", reference),
    ], limit=1)
    if not order:
        order = env["sale.order"].create({
            "partner_id": customers[(index - 1) % len(customers)].id,
            "client_order_ref": reference,
            "warehouse_id": warehouses[(index - 1) % len(warehouses)].id,
            "date_order": date(2026, 8, 15) + timedelta(days=index % 35),
            "note": "Venta confirmada generada para la comprobación del bloque 5.",
            "order_line": sale_lines(index, 3),
        })
    if order.state in ("draft", "sent"):
        order.action_confirm()
    if not order.invoice_ids:
        order._create_invoices()
    for invoice in order.invoice_ids.filtered(lambda move: move.state == "draft"):
        invoice.invoice_date = date(2026, 8, 15) + timedelta(days=index % 35)
        invoice.action_post()
    if index % 10 == 0:
        env.cr.commit()
        print(f"BLOCK5_PROGRESS sales={index}/150")


# Cien compras confirmadas, recibidas y con factura de proveedor validada.
for index in range(1, 101):
    reference = f"B5-PO-{index:03d}"
    order = env["purchase.order"].search([
        ("partner_ref", "=", reference),
    ], limit=1)
    if not order:
        warehouse = warehouses[(index - 1) % len(warehouses)]
        order = env["purchase.order"].create({
            "partner_id": suppliers[(index - 1) % len(suppliers)].id,
            "partner_ref": reference,
            "date_order": date(2026, 8, 10) + timedelta(days=index % 40),
            "picking_type_id": warehouse.in_type_id.id,
            "notes": "Compra confirmada con recepción y factura validada del bloque 5.",
            "order_line": purchase_lines(index, 3),
        })
    if order.state in ("draft", "sent", "to approve"):
        order.button_confirm()
    for picking in order.picking_ids:
        complete_picking(picking)
    if not order.invoice_ids:
        order.action_create_invoice()
    for bill in order.invoice_ids.filtered(lambda move: move.state == "draft"):
        bill.invoice_date = date(2026, 8, 10) + timedelta(days=index % 40)
        bill.action_post()
    if index % 10 == 0:
        env.cr.commit()
        print(f"BLOCK5_PROGRESS purchases={index}/100")


# Generación física de 50 facturas de venta en PDF.
pdf_directory = Path("/mnt/extra-addons/evidencias_facturas")
pdf_directory.mkdir(parents=True, exist_ok=True)
invoices = env["account.move"].search([
    ("move_type", "=", "out_invoice"),
    ("state", "=", "posted"),
    ("invoice_origin", "like", "S%"),
], order="id")
block5_invoices = invoices.filtered(
    lambda invoice: invoice.invoice_line_ids.sale_line_ids.order_id.filtered(
        lambda order: (order.client_order_ref or "").startswith("B5-SALE-")
    )
)[:50]

if len(block5_invoices) < 50:
    raise RuntimeError(f"Solo se encontraron {len(block5_invoices)} facturas de venta del bloque 5.")

report_model = env["ir.actions.report"]
for position, invoice in enumerate(block5_invoices, start=1):
    pdf_content, _ = report_model._render_qweb_pdf(
        "account.account_invoices", res_ids=[invoice.id]
    )
    filename = pdf_directory / f"factura_quetzalmart_{position:03d}.pdf"
    filename.write_bytes(pdf_content)

env.cr.commit()

print("BLOCK5_SUMMARY", {
    "sale_quotations": env["sale.order"].search_count([
        ("client_order_ref", "like", "B5-SQ-%"), ("state", "in", ("draft", "sent")),
    ]),
    "sales_confirmed": env["sale.order"].search_count([
        ("client_order_ref", "like", "B5-SALE-%"), ("state", "in", ("sale", "done")),
    ]),
    "purchase_quotations": env["purchase.order"].search_count([
        ("partner_ref", "like", "B5-PQ-%"), ("state", "in", ("draft", "sent")),
    ]),
    "purchases_confirmed": env["purchase.order"].search_count([
        ("partner_ref", "like", "B5-PO-%"), ("state", "in", ("purchase", "done")),
    ]),
    "posted_customer_invoices": env["account.move"].search_count([
        ("move_type", "=", "out_invoice"), ("state", "=", "posted"),
        ("invoice_line_ids.sale_line_ids.order_id.client_order_ref", "like", "B5-SALE-%"),
    ]),
    "posted_vendor_bills": env["account.move"].search_count([
        ("move_type", "=", "in_invoice"), ("state", "=", "posted"),
        ("invoice_line_ids.purchase_line_id.order_id.partner_ref", "like", "B5-PO-%"),
    ]),
    "pdf_files": len(list(pdf_directory.glob("factura_quetzalmart_*.pdf"))),
})
