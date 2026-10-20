"""Configuración inicial de QuetzalMart (se ejecuta una vez al instalar el módulo)."""
import base64
import logging

from odoo import Command
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

SUCURSALES = [
    # código, nombre, ciudad, calle, país, estado, código postal, teléfono, equipo de ventas
    ("GUA", "Sucursal Guatemala", "Ciudad de Guatemala", "Avenida Bolívar 32-17, Zona 4",
     "gt", "Guatemala", "01004", "+502 2385 7700"),
    ("MEX", "Sucursal México", "Tapachula", "Boulevard Belisario Domínguez 1420",
     "mx", "Chiapas", "30700", "+52 962 118 4500"),
    ("SAL", "Sucursal El Salvador", "Santa Ana", "Avenida Independencia Sur 25",
     "sv", None, "02101", "+503 2447 8800"),
]

# Sector de almacenamiento -> categorías que se guardan ahí (reglas de ubicación).
SECTORES = [
    ("secos", "Abarrotes secos", ["cat_despensa", "cat_bebidas", "cat_snacks"]),
    ("refrigerados", "Cámara de refrigeración", ["cat_lacteos"]),
    ("quimicos", "Químicos y limpieza", ["cat_limpieza"]),
    ("bazar", "Bazar y cuidado personal", ["cat_cuidado"]),
    ("materiales", "Materiales operativos", ["cat_materiales"]),
    ("cuarentena", "Cuarentena (producto no conforme)", []),
]

def registrar_xmlid(env, nombre, registro):
    """Identificador externo para que las plantillas de Excel puedan referenciarlo."""
    env["ir.model.data"]._update_xmlids([{
        "xml_id": "qm_implementacion.%s" % nombre, "record": registro, "noupdate": True,
    }])


def nombre_traducido(registro, nombre):
    """Escribe un nombre traducible en inglés y en español (si no, se ve la traducción vieja)."""
    for idioma in ("en_US", "es_419"):
        registro.with_context(lang=idioma).name = nombre


def leer_imagen(ruta):
    with file_open(ruta, "rb") as archivo:
        return base64.b64encode(archivo.read())


def post_init_hook(env):
    empresa = _configurar_empresa(env)
    _activar_ajustes(env)
    equipos = _crear_equipos(env)
    almacenes = _crear_sucursales(env, empresa, equipos)
    _crear_sectores(env, almacenes)
    _crear_ubicaciones_de_trabajo(env, almacenes)
    _configurar_tienda(env, empresa, equipos["web"])
    _configurar_envios(env, empresa)
    _configurar_pagos(env)
    _logger.info("QuetzalMart configurado: %s sucursales", len(almacenes))


def _configurar_empresa(env):
    empresa = env.ref("base.main_company")
    logo = leer_imagen("qm_implementacion/static/img/logo_quetzalmart.png")
    empresa.write({
        "name": "QuetzalMart",
        "logo": logo,
        "street": "Avenida Bolívar 32-17, Zona 4",
        "city": "Ciudad de Guatemala",
        "zip": "01004",
        "country_id": env.ref("base.gt").id,
        "phone": "+502 2385 7700",
        "email": empresa.email or "ventas@quetzalmart.example",
        "vat": "9845123-6",
        "external_report_layout_id": env.ref("web.external_layout_bold").id,
        "primary_color": "#0B6E4F",
        "secondary_color": "#C8102E",
        "font": "Montserrat",
        "report_footer": "QuetzalMart · Guatemala · México · El Salvador · Gracias por su compra",
        # Compras mayores a Q 10,000 requieren aprobación de un gerente (Manual 2).
        "po_double_validation": "two_step",
        "po_double_validation_amount": 10000,
    })
    estado_gt = env["res.country.state"].search(
        [("country_id.code", "=", "GT"), ("name", "=", "Guatemala")], limit=1)
    if estado_gt:
        empresa.state_id = estado_gt
    # Formato guatemalteco: "Q 1,250.50" (símbolo antes y punto decimal).
    env.ref("base.GTQ").position = "before"
    env["res.lang"]._activate_lang("es_419").write({"decimal_point": ".", "thousands_sep": ","})
    for moneda in ("USD", "MXN"):
        env["res.currency"].with_context(active_test=False).search(
            [("name", "=", moneda)]).active = True
    # IVA de Guatemala (l10n_gt) por defecto en ventas y compras.
    iva_venta = env["account.tax"].search([
        ("company_id", "=", empresa.id), ("type_tax_use", "=", "sale"),
        ("amount", "=", 12), ("amount_type", "=", "percent")], limit=1)
    iva_compra = env["account.tax"].search([
        ("company_id", "=", empresa.id), ("type_tax_use", "=", "purchase"),
        ("amount", "=", 12), ("amount_type", "=", "percent")], limit=1)
    if iva_venta:
        empresa.account_sale_tax_id = iva_venta
    if iva_compra:
        empresa.account_purchase_tax_id = iva_compra
    return empresa


def _activar_ajustes(env):
    ajustes = env["res.config.settings"].create({
        "group_stock_multi_locations": True,
        "group_use_lead": True,
    })
    ajustes.execute()
    # El asistente de ajustes guarda en 0 el límite de subida de OCA DMS (que por
    # defecto es 25 MB): sin esto ningún PDF podría guardarse en Documentos.
    env["ir.config_parameter"].sudo().set_param("dms.binary_max_size", 50)


def _crear_equipos(env):
    Equipo = env["crm.team"]
    equipos = {}
    # Los equipos que Odoo crea por defecto se reutilizan para no dejar equipos vacíos.
    predeterminados = {"GUA": "sales_team.team_sales_department",
                       "web": "sales_team.salesteam_website_sales"}
    for codigo, nombre in (("GUA", "Sucursal Guatemala"), ("MEX", "Sucursal México"),
                           ("SAL", "Sucursal El Salvador"), ("web", "Tienda en línea")):
        equipo = Equipo.search([("name", "=", nombre)], limit=1)
        if not equipo and codigo in predeterminados:
            equipo = env.ref(predeterminados[codigo], raise_if_not_found=False) or Equipo
        if not equipo:
            equipo = Equipo.create({"name": nombre})
        nombre_traducido(equipo, nombre)
        equipo.write({"use_leads": True, "use_opportunities": True})
        equipos[codigo] = equipo
        registrar_xmlid(env, "equipo_%s" % codigo.lower(), equipo)
    return equipos


def _crear_sucursales(env, empresa, equipos):
    Almacen = env["stock.warehouse"]
    almacenes = {}
    for codigo, nombre, ciudad, calle, pais, estado, cp, telefono in SUCURSALES:
        pais_rec = env.ref("base.%s" % pais)
        estado_rec = env["res.country.state"].search(
            [("country_id", "=", pais_rec.id), ("name", "=", estado)], limit=1) if estado else False
        direccion = env["res.partner"].create({
            "name": nombre,
            "type": "other",
            "parent_id": empresa.partner_id.id,
            "street": calle,
            "city": ciudad,
            "zip": cp,
            "state_id": estado_rec.id if estado_rec else False,
            "country_id": pais_rec.id,
            "phone": telefono,
        })
        almacen = Almacen.search([("company_id", "=", empresa.id), ("code", "=", codigo)], limit=1)
        if not almacen and codigo == "GUA":
            almacen = Almacen.search([("company_id", "=", empresa.id)], order="id", limit=1)
        valores = {"name": nombre, "code": codigo, "partner_id": direccion.id}
        if almacen:
            almacen.write(valores)
        else:
            almacen = Almacen.create(dict(valores, company_id=empresa.id))
        almacenes[codigo] = almacen
        registrar_xmlid(env, "almacen_%s" % codigo.lower(), almacen)
        registrar_xmlid(env, "direccion_%s" % codigo.lower(), direccion)
    return almacenes


def _crear_sectores(env, almacenes):
    Ubicacion = env["stock.location"]
    Regla = env["stock.putaway.rule"]
    for codigo, almacen in almacenes.items():
        for clave, nombre, categorias in SECTORES:
            sector = Ubicacion.search([
                ("location_id", "=", almacen.lot_stock_id.id), ("name", "=", nombre)], limit=1)
            if not sector:
                sector = Ubicacion.create({
                    "name": nombre,
                    "usage": "internal",
                    "location_id": almacen.lot_stock_id.id,
                    "company_id": almacen.company_id.id,
                })
            registrar_xmlid(env, "ubicacion_%s_%s" % (codigo.lower(), clave), sector)
            for xmlid in categorias:
                Regla.create({
                    "category_id": env.ref("qm_implementacion.%s" % xmlid).id,
                    "location_in_id": almacen.lot_stock_id.id,
                    "location_out_id": sector.id,
                    "company_id": almacen.company_id.id,
                })


def _crear_ubicaciones_de_trabajo(env, almacenes):
    for codigo, almacen in almacenes.items():
        ubicacion = env["hr.work.location"].search([("name", "=", almacen.name)], limit=1)
        if not ubicacion:
            ubicacion = env["hr.work.location"].create({
                "name": almacen.name,
                "location_type": "office",
                "address_id": almacen.partner_id.id,
            })
        registrar_xmlid(env, "ubicacion_trabajo_%s" % codigo.lower(), ubicacion)


def _configurar_tienda(env, empresa, equipo_web):
    sitio = env["website"].search([], order="id", limit=1)
    espanol = env["res.lang"]._activate_lang("es_419")
    sitio.write({
        "name": "QuetzalMart",
        "company_id": empresa.id,
        "logo": leer_imagen("qm_implementacion/static/img/logo_quetzalmart.png"),
        "favicon": leer_imagen("qm_implementacion/static/img/icono_quetzalmart.png"),
        "language_ids": [Command.set(espanol.ids)],
        "default_lang_id": espanol.id,
        "cookies_bar": False,
        "auth_signup_uninvited": "b2c",
        "account_on_checkout": "optional",
        "show_line_subtotals_tax_selection": "tax_included",
        "salesteam_id": equipo_web.id,
        "shop_ppg": 24,
        "shop_ppr": 4,
    })
    env["ir.config_parameter"].sudo().set_param("auth_signup.invitation_scope", "b2c")
    # Paleta de la tienda con los colores de la marca (botones verdes, acentos rojos).
    env["web_editor.assets"].make_scss_customization(
        "/website/static/src/scss/options/colors/user_color_palette.scss",
        {"o-color-1": "#0B6E4F", "o-color-2": "#C8102E", "o-color-3": "#F3F7F4",
         "o-color-4": "#FFFFFF", "o-color-5": "#064635"},
    )


def _producto_envio(env, nombre, precio):
    iva = env.company.account_sale_tax_id
    return env["product.product"].create({
        "name": nombre,
        "type": "service",
        "sale_ok": False,
        "purchase_ok": False,
        "list_price": precio,
        "invoice_policy": "order",
        "taxes_id": [Command.set(iva.ids)],
    })


def _configurar_envios(env, empresa):
    Transporte = env["delivery.carrier"]
    Transporte.search([]).write({"is_published": False, "active": False})
    gt, mx, sv = env.ref("base.gt"), env.ref("base.mx"), env.ref("base.sv")
    metodos = [
        ("Entrega a domicilio (Guatemala)", 30.0, 350.0, [gt.id],
         "Entrega de 24 a 48 horas en Guatemala. Gratis desde Q350."),
        ("Envío regional (México y El Salvador)", 85.0, 900.0, [mx.id, sv.id],
         "Entrega de 3 a 5 días hábiles. Gratis desde Q900."),
        ("Recoger en sucursal", 0.0, 0.0, [gt.id, mx.id, sv.id],
         "Recógelo sin costo en la sucursal más cercana."),
    ]
    for secuencia, (nombre, precio, gratis_desde, paises, descripcion) in enumerate(metodos, 1):
        Transporte.create({
            "name": nombre,
            "sequence": secuencia,
            "delivery_type": "fixed",
            "product_id": _producto_envio(env, nombre, precio).id,
            "fixed_price": precio,
            "free_over": bool(gratis_desde),
            "amount": gratis_desde,
            "country_ids": [Command.set(paises)],
            "carrier_description": descripcion,
            "is_published": True,
            "company_id": empresa.id,
        })


def _configurar_pagos(env):
    demo = env.ref("payment.payment_provider_demo", raise_if_not_found=False)
    if demo:
        nombre_traducido(demo, "Tarjeta de crédito o débito (modo de prueba)")
        demo.write({"state": "test", "is_published": True})
