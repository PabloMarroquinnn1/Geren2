"""Create one clearly marked demo invoice and verify DMS auto-archiving."""

import re

from odoo import fields


reference = "DMS-AUTO-TEST-2026-09-29"
Move = env["account.move"].sudo()
invoice = Move.search(
    [("move_type", "=", "out_invoice"), ("ref", "=", reference)], limit=1
)

if not invoice:
    company = env.company
    partner = env["res.partner"].sudo().search(
        [("name", "=", "Cliente de prueba - archivo automático DMS")], limit=1
    )
    if not partner:
        partner = env["res.partner"].sudo().create(
            {
                "name": "Cliente de prueba - archivo automático DMS",
                "company_type": "person",
                "email": False,
                "phone": False,
                "comment": "Registro técnico de prueba de archivado automático; no enviar ni cobrar.",
            }
        )

    product = env["product.product"].sudo().search(
        [("default_code", "=", "RPA-DEMO-001")], limit=1
    )
    if not product:
        product = env["product.product"].sudo().search(
            [("name", "ilike", "RPA Demo Arroz 1 kg")], limit=1
        )
    assert product, "No se encontró el producto demo RPA Demo Arroz 1 kg"

    invoice = Move.create(
        {
            "move_type": "out_invoice",
            "company_id": company.id,
            "partner_id": partner.id,
            "invoice_date": fields.Date.context_today(partner),
            "ref": reference,
            "invoice_origin": "PRUEBA ARCHIVO AUTOMÁTICO DMS",
            "narration": "Prueba técnica de archivo PDF en Documentos. No enviar ni cobrar.",
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "name": "Prueba de archivado PDF automático en Documentos; no enviar ni cobrar",
                        "quantity": 1,
                        "price_unit": 1.00,
                    },
                )
            ],
        }
    )

if invoice.state != "posted":
    invoice.action_post()
else:
    invoice._archive_posted_invoices_in_documents()

root = env["dms.directory"].sudo().search(
    [("name", "=", "Documentos QuetzalMart"), ("is_root_directory", "=", True)],
    limit=1,
)
directory = env["dms.directory"].sudo().search(
    [("name", "=", "Facturas PDF"), ("parent_id", "=", root.id)], limit=1
)
safe_reference = re.sub(r"[^A-Za-z0-9._-]+", "_", invoice.name).strip("_.")
filename = f"{safe_reference or 'factura_' + str(invoice.id)}.pdf"
archived = env["dms.file"].sudo().search(
    [
        ("directory_id", "=", directory.id),
        ("name", "=", filename),
    ],
    limit=1,
)
assert invoice.state == "posted", f"La factura quedó en estado {invoice.state}"
assert archived, "No apareció el PDF de prueba en la carpeta Facturas PDF"
assert archived.mimetype == "application/pdf" and archived.size > 1000
env.cr.commit()
print(
    "DMS_AUTO_ARCHIVE_TEST",
    {
        "invoice_id": invoice.id,
        "invoice_number": invoice.name,
        "invoice_reference": invoice.ref,
        "invoice_state": invoice.state,
        "amount_total": invoice.amount_total,
        "dms_file_id": archived.id,
        "dms_file": archived.name,
        "directory": archived.directory_id.complete_name,
        "pdf_size": archived.size,
        "total_pdf_in_directory": env["dms.file"].sudo().search_count(
            [
                ("directory_id", "=", directory.id),
                ("mimetype", "=", "application/pdf"),
            ]
        ),
    },
)
