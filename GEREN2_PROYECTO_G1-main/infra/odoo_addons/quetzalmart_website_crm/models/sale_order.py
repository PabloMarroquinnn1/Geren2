import logging

from odoo import _, fields, models


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    qm_campaign_sent_at = fields.Datetime(
        string="QuetzalMart post-purchase campaign sent at",
        copy=False,
        readonly=True,
    )

    def action_confirm(self):
        result = super().action_confirm()
        self._qm_link_website_orders_to_crm()
        return result

    def _qm_link_website_orders_to_crm(self):
        """Create a won CRM opportunity and link it to each confirmed web order."""
        orders = self.sudo().filtered(
            lambda order: order.website_id
            and order.state in ("sale", "done")
            and order.partner_id
            and not order.opportunity_id
        )
        if not orders:
            return

        Lead = self.env["crm.lead"].sudo()
        Team = self.env["crm.team"].sudo()
        Stage = self.env["crm.stage"].sudo()

        for order in orders:
            try:
                with self.env.cr.savepoint():
                    team = order.team_id or Team.search(
                        [
                            ("company_id", "in", [order.company_id.id, False]),
                        ],
                        order="id",
                        limit=1,
                    )
                    stage_domain = [("is_won", "=", True)]
                    if team:
                        stage_domain += [
                            "|",
                            ("team_id", "=", team.id),
                            ("team_id", "=", False),
                        ]
                    won_stage = Stage.search(
                        stage_domain,
                        order="sequence, id",
                        limit=1,
                    )

                    values = {
                        "name": _("Website purchase %(order)s - %(customer)s")
                        % {
                            "order": order.name,
                            "customer": order.partner_id.display_name,
                        },
                        "type": "opportunity",
                        "partner_id": order.partner_id.id,
                        "expected_revenue": order.amount_total,
                        "company_id": order.company_id.id,
                        "description": _(
                            "Automatically linked to the confirmed QuetzalMart website order %(order)s."
                        )
                        % {"order": order.name},
                    }
                    if team:
                        values["team_id"] = team.id
                    if won_stage:
                        values.update({"stage_id": won_stage.id, "probability": 100.0})
                    if order.user_id:
                        values["user_id"] = order.user_id.id
                    if order.source_id:
                        values["source_id"] = order.source_id.id
                    if order.medium_id:
                        values["medium_id"] = order.medium_id.id
                    if order.campaign_id:
                        values["campaign_id"] = order.campaign_id.id

                    opportunity = Lead.create(values)
                    order.write({"opportunity_id": opportunity.id})
                    _logger.info(
                        "Linked website order %s to CRM opportunity %s",
                        order.name,
                        opportunity.id,
                    )
            except Exception:
                # A CRM-side problem must not roll back a customer's confirmed order.
                _logger.exception(
                    "Could not create a CRM opportunity for website order %s",
                    order.name,
                )

    def _qm_send_post_purchase_campaign(self):
        """Send the existing marketing creative once, after the invoice mail succeeds."""
        self.ensure_one()
        if (
            self.qm_campaign_sent_at
            or not self.website_id
            or not self.opportunity_id
            or not self.partner_id.email
        ):
            return False

        mailing = self.env["mailing.mailing"].sudo().search(
            [
                ("subject", "=", "QuetzalMart | Beneficios de temporada y compra segura"),
                ("state", "=", "done"),
            ],
            order="id desc",
            limit=1,
        )
        if not mailing or not mailing.body_html:
            _logger.warning("No sent QuetzalMart campaign creative is available for %s", self.name)
            return False

        message = self.env["mail.mail"].sudo().create(
            {
                "subject": mailing.subject,
                "body_html": mailing.body_html,
                "email_from": mailing.email_from,
                "email_to": self.partner_id.email,
                "model": "crm.lead",
                "res_id": self.opportunity_id.id,
                "auto_delete": False,
            }
        )
        message.send(raise_exception=True)
        if message.state != "sent":
            raise RuntimeError("The post-purchase campaign was not sent for %s" % self.name)
        self.qm_campaign_sent_at = fields.Datetime.now()
        _logger.info(
            "Sent QuetzalMart campaign after invoice for order %s to partner %s",
            self.name,
            self.partner_id.id,
        )
        return True
