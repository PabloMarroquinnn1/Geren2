from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _send_invoice(self):
        # Primero sale el correo con la factura (estándar de Odoo) y luego se
        # programa la campaña de marketing para ese mismo cliente.
        resultado = super()._send_invoice()
        pedidos = self.sale_order_ids.filtered(lambda pedido: pedido.state == "sale")
        pedidos._qm_programar_campana()
        return resultado
