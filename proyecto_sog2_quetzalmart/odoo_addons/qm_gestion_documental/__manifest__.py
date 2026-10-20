{
    "name": "QuetzalMart - Gestión documental",
    "summary": "Estructura del archivo digital (OCA DMS) y archivo automático "
               "del PDF de cada factura publicada.",
    "version": "18.0.1.0.0",
    "category": "Document Management",
    "author": "QuetzalMart SOG2",
    "license": "LGPL-3",
    "depends": ["account", "sale", "dms"],
    "data": [
        "data/parametros.xml",
        "data/estructura_archivo.xml",
        "data/cron.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
}
