from odoo import Command
from odoo.tools import file_open

CODIGO_PROMOCIONAL = "QUETZAL10"


def post_init_hook(env):
    parametros = env["ir.config_parameter"].sudo()
    # Al pagar en la web: factura automática + correo con la plantilla propia.
    parametros.set_param("sale.automatic_invoice", "True")
    parametros.set_param(
        "sale.default_invoice_email_template",
        env.ref("qm_crm_postventa.plantilla_factura").id,
    )

    with file_open("qm_crm_postventa/data/campana_masiva.html") as archivo:
        cuerpo = archivo.read()
    env.ref("qm_crm_postventa.correo_masivo_temporada").write({
        "body_arch": cuerpo,
        "body_html": cuerpo,
    })

    _crear_codigo_promocional(env)


def _crear_codigo_promocional(env):
    """Código QUETZAL10: 10 % de descuento en el pedido (tienda en línea y ventas)."""
    if env["loyalty.rule"].search_count([("code", "=", CODIGO_PROMOCIONAL)]):
        return
    # La regla y la recompensa se crean explícitamente: Odoo solo las propone
    # por defecto en el formulario, no al crear el programa por código.
    env["loyalty.program"].create({
        "name": "Campaña postcompra: 10% con QUETZAL10",
        "program_type": "promo_code",
        "trigger": "with_code",
        "applies_on": "current",
        "rule_ids": [Command.create({
            "mode": "with_code",
            "code": CODIGO_PROMOCIONAL,
            "minimum_amount": 0,
            "reward_point_amount": 1,
            "reward_point_mode": "order",
        })],
        "reward_ids": [Command.create({
            "reward_type": "discount",
            "discount": 10,
            "discount_mode": "percent",
            "discount_applicability": "order",
            "required_points": 1,
        })],
    })
