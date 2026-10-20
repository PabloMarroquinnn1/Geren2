from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_google_analytics_data(self, product, combination_info):
        # view_item y add_to_cart: el SKU (QM-...) es más legible en los informes
        # de GA4 que el id interno o el código de barras.
        datos = super()._get_google_analytics_data(product, combination_info)
        datos["item_id"] = product.default_code or str(product.id)
        datos["item_brand"] = "QuetzalMart"
        if self.public_categ_ids:
            datos["item_category2"] = self.public_categ_ids[0].name
        return datos
