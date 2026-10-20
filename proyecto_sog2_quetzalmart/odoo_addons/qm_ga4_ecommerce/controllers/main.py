from odoo.addons.website_sale.controllers.main import WebsiteSale


class QmWebsiteSaleGa4(WebsiteSale):

    def order_2_return_dict(self, order):
        # Evento purchase de la página de confirmación: mismos item_id (SKU) que
        # en view_item/add_to_cart para que GA4 sume correctamente por producto.
        datos = super().order_2_return_dict(order)
        datos["transaction_id"] = order.name
        datos["items"] = order._qm_ga4_items()
        return datos
