{
    "name": "QuetzalMart - Google Analytics 4 (comercio electrónico)",
    "summary": "Completa el embudo GA4 de la tienda: begin_checkout, view_cart, "
               "remove_from_cart, add_shipping_info y add_payment_info, con SKU "
               "como item_id y propiedades de usuario para segmentar.",
    "version": "18.0.1.0.0",
    "category": "Website/eCommerce",
    "author": "QuetzalMart SOG2",
    "license": "LGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "qm_ga4_ecommerce/static/src/js/qm_ga4.js",
        ],
    },
    "installable": True,
}
