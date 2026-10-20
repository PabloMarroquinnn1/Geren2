import base64
import logging
import re

from odoo import _, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        result = super().action_post()
        self._archive_posted_invoices_in_documents()
        return result

    def _archive_posted_invoices_in_documents(self):
        invoices = self.filtered(
            lambda move: move.state == "posted"
            and move.move_type in ("out_invoice", "in_invoice")
        )
        if not invoices:
            return

        Directory = self.env["dms.directory"].sudo()
        root = Directory.search(
            [
                ("name", "=", "Documentos QuetzalMart"),
                ("is_root_directory", "=", True),
            ],
            limit=1,
        )
        if not root:
            raise UserError(
                _("No existe la carpeta raíz Documentos QuetzalMart en la app Documentos.")
            )

        directory = Directory.search(
            [("name", "=", "Facturas PDF"), ("parent_id", "=", root.id)],
            limit=1,
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

        File = self.env["dms.file"].sudo()
        Category = self.env["dms.category"].sudo()
        Tag = self.env["dms.tag"].sudo()
        year_tag = Tag.search([("name", "=", "2026")], limit=1)
        if not year_tag:
            year_tag = Tag.create({"name": "2026"})

        report = self.env["ir.actions.report"].sudo()
        for invoice in invoices:
            is_customer_invoice = invoice.move_type == "out_invoice"
            category_name = (
                "Factura de cliente" if is_customer_invoice else "Factura de proveedor"
            )
            category = Category.search([("name", "=", category_name)], limit=1)
            if not category:
                category = Category.create({"name": category_name})

            type_tag_name = "Factura de venta" if is_customer_invoice else "Factura de proveedor"
            type_tag = Tag.search([("name", "=", type_tag_name)], limit=1)
            if not type_tag:
                type_tag = Tag.create({"name": type_tag_name})

            report_pdf, _content_type = report._render_qweb_pdf(
                "account.account_invoices", res_ids=[invoice.id]
            )
            if not report_pdf or not report_pdf.startswith(b"%PDF-"):
                raise UserError(
                    _("No se pudo generar el PDF de la factura %(invoice)s.")
                    % {"invoice": invoice.display_name}
                )

            safe_reference = re.sub(r"[^A-Za-z0-9._-]+", "_", invoice.name).strip("_.")
            filename = f"{safe_reference or 'factura_' + str(invoice.id)}.pdf"
            values = {
                "name": filename,
                "directory_id": directory.id,
                "category_id": category.id,
                "tag_ids": [(6, 0, [type_tag.id, year_tag.id])],
                "content": base64.b64encode(report_pdf),
                "mimetype": "application/pdf",
            }
            existing = File.search(
                [
                    ("directory_id", "=", directory.id),
                    ("name", "=", filename),
                ],
                limit=1,
            )
            if existing:
                existing.write(values)
                document = existing
            else:
                document = File.create(values)
            _logger.info(
                "Archived posted invoice %s as DMS file %s (id=%s)",
                invoice.name,
                document.name,
                document.id,
            )
