{
    "name": "QuetzalMart - CRM y marketing postventa",
    "summary": "Registro web y compras en línea al CRM; correo de factura con diseño "
               "propio y, después, la campaña de marketing con código de descuento.",
    "version": "18.0.1.0.0",
    "category": "Marketing",
    "author": "QuetzalMart SOG2",
    "license": "LGPL-3",
    "depends": [
        "website_sale",
        "website_sale_loyalty",
        "sale_crm",
        "website_crm",
        "mass_mailing",
        "auth_signup",
        "account_payment",
    ],
    "data": [
        "data/crm_marketing_data.xml",
        "data/correo_factura.xml",
        "data/correo_campana.xml",
        "data/campana_masiva.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
