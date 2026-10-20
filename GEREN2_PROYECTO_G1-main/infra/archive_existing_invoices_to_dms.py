"""Import the existing 50 invoice PDFs into the Odoo DMS archive folder."""

import base64
import hashlib
from pathlib import Path


source = Path("/mnt/extra-addons/evidencias_facturas")
pdf_paths = sorted(source.glob("factura_quetzalmart_*.pdf"))
assert source.is_dir(), f"No existe la carpeta de origen {source}"
assert len(pdf_paths) == 50, f"Se esperaban 50 PDF; se encontraron {len(pdf_paths)}"

Move = env["account.move"].sudo()
posted_sales = Move.search(
    [
        ("move_type", "=", "out_invoice"),
        ("state", "=", "posted"),
        ("invoice_origin", "like", "S%"),
    ],
    order="id",
)
invoices = posted_sales.filtered(
    lambda move: move.invoice_line_ids.sale_line_ids.order_id.filtered(
        lambda order: (order.client_order_ref or "").startswith("B5-SALE-")
    )
)[:50]
assert len(invoices) == 50, f"Se esperaban 50 facturas origen; hay {len(invoices)}"

Directory = env["dms.directory"].sudo()
root = Directory.search(
    [
        ("name", "=", "Documentos QuetzalMart"),
        ("is_root_directory", "=", True),
    ],
    limit=1,
)
assert root, "No existe la carpeta raíz Documentos QuetzalMart"

directory = Directory.search(
    [("name", "=", "Facturas PDF"), ("parent_id", "=", root.id)], limit=1
)
if not directory:
    directory = Directory.create(
        {
            "name": "Facturas PDF",
            "storage_id": root.storage_id.id,
            "parent_id": root.id,
            "company_id": root.company_id.id,
        }
    )

Category = env["dms.category"].sudo()
category = Category.search([("name", "=", "Factura de cliente")], limit=1)
if not category:
    category = Category.create({"name": "Factura de cliente"})

Tag = env["dms.tag"].sudo()
tags = []
for tag_name in ("Factura de venta", "2026"):
    tag = Tag.search([("name", "=", tag_name)], limit=1)
    if not tag:
        tag = Tag.create({"name": tag_name})
    tags.append(tag.id)

File = env["dms.file"].sudo()
created = 0
already_present = 0
for path, invoice in zip(pdf_paths, invoices):
    content = path.read_bytes()
    assert content.startswith(b"%PDF-"), f"El archivo no parece PDF: {path.name}"
    values = {
        "name": path.name,
        "directory_id": directory.id,
        "category_id": category.id,
        "tag_ids": [(6, 0, tags)],
        "content": base64.b64encode(content),
        "mimetype": "application/pdf",
    }
    existing = File.search(
        [("directory_id", "=", directory.id), ("name", "=", path.name)], limit=1
    )
    if existing:
        expected_checksum = hashlib.sha1(content).hexdigest()
        if existing.checksum != expected_checksum:
            raise RuntimeError(
                f"Ya existe {path.name} con contenido distinto en Facturas PDF."
            )
        already_present += 1
        continue
    File.create(values)
    created += 1

env.cr.commit()
print(
    "DMS_INVOICE_IMPORT",
    {
        "directory_id": directory.id,
        "directory": directory.complete_name,
        "created": created,
        "already_present": already_present,
        "pdf_total": File.search_count(
            [("directory_id", "=", directory.id), ("mimetype", "=", "application/pdf")]
        ),
    },
)
