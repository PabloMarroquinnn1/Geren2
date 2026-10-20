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
    Programa = env["loyalty.program"]
    if env["loyalty.rule"].search_count([("code", "=", CODIGO_PROMOCIONAL)]):
        return
    programa = Programa.create({
        "name": "Campaña postcompra: 10% con QUETZAL10",
        "program_type": "promo_code",
        "trigger": "with_code",
        "applies_on": "current",
    })
    programa.rule_ids.write({"code": CODIGO_PROMOCIONAL, "minimum_amount": 0})
    programa.reward_ids.write({
        "reward_type": "discount",
        "discount": 10,
        "discount_mode": "percent",
        "discount_applicability": "order",
    })
