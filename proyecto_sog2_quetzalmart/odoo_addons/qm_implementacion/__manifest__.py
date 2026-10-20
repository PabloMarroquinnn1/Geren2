{
    "name": "QuetzalMart - Implementación",
    "summary": "Instala y configura el ERP de QuetzalMart: ventas, compras, inventario, "
               "facturación, empleados, CRM, tienda en línea, marketing y documentos.",
    "description": """
Un solo módulo para dejar lista la implementación:

* Compañía QuetzalMart (Guatemala, quetzales, plan contable l10n_gt).
* Tres sucursales (almacenes) con sectores de almacenamiento y reglas de ubicación.
* Equipos de venta por sucursal y equipo de la tienda en línea.
* Tienda en línea con portada, categorías, envíos y pago de prueba.
* Módulos propios: puente RPA, gestión documental, GA4 y marketing postventa.
""",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "author": "QuetzalMart SOG2",
    "license": "LGPL-3",
    "depends": [
        # Módulos del enunciado
        "sale_management",
        "purchase",
        "purchase_stock",
        "stock",
        "account",
        "l10n_gt",
        "hr",
        "hr_contract",
        "crm",
        "contacts",
        "website_sale",
        "website_sale_stock",
        "mass_mailing",
        "website_mass_mailing",
        "payment_demo",
        "dms",
        # Módulos propios
        "qm_puente_rpa",
        "qm_gestion_documental",
        "qm_ga4_ecommerce",
        "qm_crm_postventa",
    ],
    "data": [
        "data/categorias.xml",
        "views/sitio_web.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
