import logging

from odoo import models


_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _postprocess_sent_message(self, success_pids, failure_reason=False, failure_type=None):
        # Odoo calls this only after the SMTP attempt. Record the invoice IDs
        # before super() possibly removes auto-deleted outgoing mail records.
        invoice_ids = [
            mail.mail_message_id.res_id
            for mail in self
            if mail.state == "sent"
            and mail.mail_message_id.model == "account.move"
            and mail.mail_message_id.res_id
        ]
        result = super()._postprocess_sent_message(
            success_pids,
            failure_reason=failure_reason,
            failure_type=failure_type,
        )
        if failure_type or not invoice_ids:
            return result

        Invoice = self.env["account.move"].sudo()
        SaleOrder = self.env["sale.order"].sudo()
        for invoice in Invoice.browse(invoice_ids).exists():
            if invoice.move_type != "out_invoice" or invoice.state != "posted":
                continue
            orders = invoice.invoice_line_ids.sale_line_ids.order_id
            if not orders and invoice.invoice_origin:
                orders = SaleOrder.search(
                    [("name", "=", invoice.invoice_origin)], limit=1
                )
            for order in orders.filtered(lambda record: record.website_id):
                try:
                    with self.env.cr.savepoint():
                        order._qm_send_post_purchase_campaign()
                except Exception:
                    # A marketing failure must not reverse an already delivered
                    # customer invoice or stop the remaining invoice batch.
                    _logger.exception(
                        "Could not send post-purchase campaign for %s", order.name
                    )
        return result
