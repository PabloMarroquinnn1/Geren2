import json

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _qm_ga4_items(self):
        self.ensure_one()
        lineas = self.order_line.filtered(
            lambda linea: linea.product_id and not linea.display_type and not linea.is_delivery
        )
        items = []
        for linea in lineas:
            producto = linea.product_id
            item = {
                "item_id": producto.default_code or str(producto.id),
                "item_name": producto.name,
                "item_brand": "QuetzalMart",
                "item_category": producto.categ_id.name or "",
                "price": round(linea.price_reduce_taxexcl, 2),
                "quantity": linea.product_uom_qty,
            }
            if producto.public_categ_ids:
                item["item_category2"] = producto.public_categ_ids[0].name
            items.append(item)
        return items

    def _qm_ga4_datos_json(self):
        """Datos del carrito que el JavaScript envía a GA4 en cada paso del pago."""
        self.ensure_one()
        items = self._qm_ga4_items()
        productos = [
            linea.product_id.id for linea in self.order_line.filtered(
                lambda linea: linea.product_id and not linea.display_type and not linea.is_delivery)
        ]
        return json.dumps({
            "order_id": self.id,
            "currency": self.currency_id.name,
            "value": round(sum(item["price"] * item["quantity"] for item in items), 2),
            "items": items,
            "product_ids": productos,
            "shipping_tier": self.carrier_id.name or "",
        })
