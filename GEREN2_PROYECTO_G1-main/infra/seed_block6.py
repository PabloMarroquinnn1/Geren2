import base64
from pathlib import Path


ASSET_DIR = Path("/mnt/extra-addons/block6_assets")


def encoded(filename):
    return base64.b64encode((ASSET_DIR / filename).read_bytes())


def upsert_attachment(name, filename, res_model, res_id):
    attachment = env["ir.attachment"].sudo().search([
        ("name", "=", name),
        ("res_model", "=", res_model),
        ("res_id", "=", res_id),
    ], limit=1)
    values = {
        "name": name,
        "datas": encoded(filename),
        "mimetype": "image/png",
        "public": True,
        "res_model": res_model,
        "res_id": res_id,
    }
    if attachment:
        attachment.write(values)
    else:
        attachment = env["ir.attachment"].sudo().create(values)
    return attachment


company = env.company
website = env["website"].search([], limit=1)
if not website:
    raise RuntimeError("No existe un sitio web para configurar.")

spanish = env["res.lang"].search([("code", "=", "es_419"), ("active", "=", True)], limit=1)
if not spanish:
    raise RuntimeError("El idioma es_419 debe estar activo antes de configurar el portal.")

logo = encoded("logo-quetzalmart.png")
hero = upsert_attachment(
    "QuetzalMart - imagen principal", "hero-quetzalmart.png", "website", website.id
)

company.write({
    "logo": logo,
    "street": "Zona 10",
    "city": "Ciudad de Guatemala",
    "country_id": env.ref("base.gt").id,
    "email": "info@quetzalmart.local",
    "phone": "+502 2200 2026",
})
company.partner_id.write({"image_1920": logo})

website_values = {
    "name": "QuetzalMart",
    "domain": "https://quetzalmart.34-9-149-41.sslip.io",
    "logo": logo,
    "default_lang_id": spanish.id,
    "language_ids": [(6, 0, [spanish.id])],
    "shop_ppg": 24,
    "shop_ppr": 4,
    "shop_default_sort": "website_sequence asc",
    "social_default_image": encoded("hero-quetzalmart.png"),
    "cookies_bar": True,
}
website.write(website_values)

# Catálogo: fotografías, descripciones y orden consistente por familia.
category_assets = {
    "Abarrotes": "categoria-abarrotes.png",
    "Bebidas": "categoria-bebidas.png",
    "Limpieza": "categoria-limpieza.png",
    "Hogar": "categoria-hogar.png",
    "Cuidado personal": "categoria-cuidado-personal.png",
    "Tecnología": "categoria-tecnologia.png",
}
category_copy = {
    "Abarrotes": "Despensa esencial para preparar comidas nutritivas todos los días.",
    "Bebidas": "Opciones refrescantes para acompañar cada momento.",
    "Limpieza": "Soluciones prácticas para mantener cada espacio impecable.",
    "Hogar": "Artículos funcionales que hacen más cómoda la vida diaria.",
    "Cuidado personal": "Bienestar y cuidado para toda la familia.",
    "Tecnología": "Accesorios confiables para trabajar, estudiar y disfrutar.",
}

sequence = 10
for category_name, asset_name in category_assets.items():
    image = encoded(asset_name)
    public_category = env["product.public.category"].search([
        ("name", "=", category_name),
    ], limit=1)
    if public_category and "image_1920" in public_category._fields:
        public_category.write({"image_1920": image})

    templates = env["product.template"].search([
        ("default_code", "like", "QM-%"),
        ("categ_id.name", "=", category_name),
    ], order="default_code")
    for template in templates:
        values = {
            "image_1920": image,
            "website_sequence": sequence,
            "is_published": True,
            "description_sale": f"{template.name}. {category_copy[category_name]}",
        }
        if "description_ecommerce" in template._fields:
            values["description_ecommerce"] = (
                f"<p><strong>{template.name}</strong></p>"
                f"<p>{category_copy[category_name]} Producto seleccionado por QuetzalMart "
                "por su buena relación entre calidad y precio.</p>"
            )
        template.write(values)
        sequence += 10

# Método de envío con tarifa fija y envío gratis para compras desde Q300.
sale_tax = env["account.tax"].search([
    ("company_id", "=", company.id),
    ("type_tax_use", "=", "sale"),
    ("amount", "=", 12.0),
], limit=1)
shipping_product = env["product.template"].search([
    ("default_code", "=", "QM-ENVIO"),
], limit=1)
shipping_values = {
    "name": "Envío estándar QuetzalMart",
    "default_code": "QM-ENVIO",
    "sale_ok": False,
    "purchase_ok": False,
    "list_price": 25.0,
}
if "type" in env["product.template"]._fields:
    shipping_values["type"] = "service"
if sale_tax:
    shipping_values["taxes_id"] = [(6, 0, [sale_tax.id])]
if shipping_product:
    shipping_product.write(shipping_values)
else:
    shipping_product = env["product.template"].create(shipping_values)

carrier = env["delivery.carrier"].search([
    ("name", "=", "Envío estándar QuetzalMart"),
    ("company_id", "=", company.id),
], limit=1)
carrier_values = {
    "name": "Envío estándar QuetzalMart",
    "company_id": company.id,
    "delivery_type": "fixed",
    "product_id": shipping_product.product_variant_id.id,
    "fixed_price": 25.0,
    "free_over": True,
    "amount": 300.0,
    "is_published": True,
    "website_id": website.id,
    "country_ids": [(6, 0, [
        env.ref("base.gt").id,
        env.ref("base.mx").id,
        env.ref("base.sv").id,
    ])],
    "website_description": (
        "Entrega estándar a Guatemala, México y El Salvador. "
        "Tarifa Q25; gratis en compras desde Q300."
    ),
}
if carrier:
    carrier.write(carrier_values)
else:
    carrier = env["delivery.carrier"].create(carrier_values)
env["delivery.carrier"].search([
    ("id", "!=", carrier.id),
    ("is_published", "=", True),
]).write({"is_published": False})

# Proveedor de pago de demostración para comprobar el evento de compra sin cobro real.
demo_provider = env["payment.provider"].search([("code", "=", "demo")], limit=1)
if demo_provider:
    demo_provider.write({"state": "test", "company_id": company.id})
if "automatic_invoice" in env["res.config.settings"]._fields:
    env["res.config.settings"].create({"automatic_invoice": True}).execute()

# Menú principal en español.
for url, name, sequence_value in (
    ("/", "Inicio", 10),
    ("/shop", "Tienda", 20),
    ("/contactus", "Contacto", 30),
):
    menu = env["website.menu"].search([
        ("website_id", "=", website.id), ("url", "=", url),
    ], limit=1)
    if menu:
        menu.with_context(lang="es_419").write({"name": name, "sequence": sequence_value})

category_links = []
for category_name in category_assets:
    category = env["product.public.category"].search([("name", "=", category_name)], limit=1)
    if category:
        category_links.append(
            f'<a class="qm-category" href="/shop?category={category.id}">'
            f'<span>{category_name}</span><small>{category_copy[category_name]}</small></a>'
        )

homepage = env.ref("website.homepage")
homepage_arch = f"""
<t name="Homepage" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">
      <style>
        :root{{--qm-plum:#5f1238;--qm-coral:#ff6247;--qm-green:#178b57;--qm-cream:#fff8ef;--qm-ink:#271923}}
        .qm-hero{{min-height:610px;background-image:linear-gradient(90deg,rgba(255,248,239,.98) 0%,rgba(255,248,239,.90) 34%,rgba(255,248,239,.12) 65%),url('/web/content/{hero.id}');background-size:cover;background-position:center;display:flex;align-items:center}}
        .qm-kicker{{display:inline-flex;gap:.5rem;align-items:center;padding:.45rem .8rem;border-radius:999px;background:#fff;color:var(--qm-green);font-weight:700;box-shadow:0 8px 25px rgba(39,25,35,.08)}}
        .qm-title{{font-size:clamp(3rem,7vw,6.3rem);line-height:.92;letter-spacing:-.055em;color:var(--qm-plum);max-width:760px;margin:1.4rem 0}}
        .qm-lead{{max-width:610px;font-size:1.2rem;color:#5c4b55}}
        .qm-btn{{display:inline-block;border-radius:14px;padding:.9rem 1.35rem;font-weight:700;text-decoration:none;margin:.5rem .5rem .5rem 0}}
        .qm-btn-primary{{background:var(--qm-coral);color:white;box-shadow:0 12px 30px rgba(255,98,71,.28)}}
        .qm-btn-secondary{{background:white;color:var(--qm-plum);border:1px solid #eadbd3}}
        .qm-section{{padding:88px 0;background:var(--qm-cream)}}
        .qm-heading{{color:var(--qm-plum);font-size:clamp(2rem,4vw,3.5rem);letter-spacing:-.035em}}
        .qm-category-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:34px}}
        .qm-category{{min-height:190px;border-radius:24px;padding:26px;background:white;color:var(--qm-ink);text-decoration:none;display:flex;flex-direction:column;justify-content:flex-end;border:1px solid #f1e6df;transition:.2s ease;box-shadow:0 10px 32px rgba(78,35,57,.06)}}
        .qm-category:hover{{transform:translateY(-5px);box-shadow:0 18px 40px rgba(78,35,57,.12);color:var(--qm-plum)}}
        .qm-category span{{font-size:1.45rem;font-weight:800}}
        .qm-category small{{font-size:.95rem;color:#74636c;margin-top:.5rem}}
        .qm-values{{background:var(--qm-plum);color:white;padding:72px 0}}
        .qm-value-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}}
        .qm-value{{padding:28px;border:1px solid rgba(255,255,255,.16);border-radius:22px;background:rgba(255,255,255,.06)}}
        .qm-value strong{{font-size:1.2rem;display:block;margin-bottom:.55rem}}
        @media(max-width:900px){{.qm-hero{{min-height:520px;background-image:linear-gradient(rgba(255,248,239,.93),rgba(255,248,239,.88)),url('/web/content/{hero.id}')}}.qm-category-grid,.qm-value-grid{{grid-template-columns:1fr}}}}
      </style>
      <section class="qm-hero">
        <div class="container">
          <span class="qm-kicker">✦ Calidad cercana, precios justos</span>
          <h1 class="qm-title">Todo lo que necesitas, más cerca de ti.</h1>
          <p class="qm-lead">Compra alimentos, bebidas, artículos para el hogar y tecnología desde Guatemala, México y El Salvador.</p>
          <div class="mt-4">
            <a class="qm-btn qm-btn-primary" href="/shop">Explorar productos</a>
            <a class="qm-btn qm-btn-secondary" href="/contactus">Hablar con nosotros</a>
          </div>
        </div>
      </section>
      <section class="qm-section">
        <div class="container">
          <p class="text-uppercase fw-bold" style="color:var(--qm-green);letter-spacing:.16em">Nuestro catálogo</p>
          <h2 class="qm-heading">Una tienda para cada parte de tu día</h2>
          <p class="qm-lead">Encuentra 60 productos seleccionados y disponibles para compra en línea.</p>
          <div class="qm-category-grid">{''.join(category_links)}</div>
        </div>
      </section>
      <section class="qm-values">
        <div class="container qm-value-grid">
          <div class="qm-value"><strong>Compra segura</strong><span>Proceso de pago protegido y comprobante electrónico.</span></div>
          <div class="qm-value"><strong>Inventario centralizado</strong><span>Disponibilidad gestionada directamente desde Odoo.</span></div>
          <div class="qm-value"><strong>Envío regional</strong><span>Entrega en Guatemala, México y El Salvador; gratis desde Q300.</span></div>
        </div>
      </section>
    </div>
  </t>
</t>
"""
for language in ("en_US", "es_419"):
    homepage.with_context(lang=language).write({"arch_db": homepage_arch})
for page in env["website.page"].search([("url", "=", "/")]):
    for language in ("en_US", "es_419"):
        page.view_id.with_context(lang=language).write({"arch_db": homepage_arch})

# Sustituir los textos de demostración del encabezado y pie de página.
layout_replacements = {
    "en_US": {
        "info@yourcompany.example.com": "info@quetzalmart.local",
        "+1 555-555-5556": "+502 2200 2026",
        "We are a team of passionate people whose goal is to improve everyone's life through disruptive products. We build great products to solve your business problems.\n                            <br/><br/>Our products are designed for small to medium size companies willing to optimize their performance.":
            "QuetzalMart acerca productos cotidianos de calidad a las familias de la región.\n                            <br/><br/>Operamos desde Guatemala con sucursales para México y El Salvador.",
    },
    "es_419": {
        "info@yourcompany.example.com": "info@quetzalmart.local",
        "info@tuempresa.ejemplo.com": "info@quetzalmart.local",
        "info@suempresa.ejemplo.com": "info@quetzalmart.local",
        "+1 555-555-5556": "+502 2200 2026",
        "Somos un equipo de personas apasionadas cuyo objetivo es mejorar la vida de todos a través de productos revolucionarios. Creamos productos para resolver sus problemas empresariales.\n                            <br/><br/>Estos productos están diseñados para pequeñas y medianas empresas dispuestas a optimizar su rendimiento.":
            "QuetzalMart acerca productos cotidianos de calidad a las familias de la región.\n                            <br/><br/>Operamos desde Guatemala con sucursales para México y El Salvador.",
    },
}
for xml_id in ("website.footer_custom", "website.header_text_element"):
    view = env.ref(xml_id)
    for language, replacements in layout_replacements.items():
        arch = view.with_context(lang=language).arch_db
        for source, target in replacements.items():
            arch = arch.replace(source, target)
        arch = arch.replace("QuetzalMart brings quality everyday products closer to families across the region.", "QuetzalMart acerca productos cotidianos de calidad a las familias de la región.")
        arch = arch.replace("We operate from Guatemala with branches serving Mexico and El Salvador.", "Operamos desde Guatemala con sucursales para México y El Salvador.")
        arch = arch.replace('<li><a href="#">Products</a></li>', '<li><a href="/shop">Productos</a></li>')
        arch = arch.replace('<li><a href="#">Productos</a></li>', '<li><a href="/shop">Productos</a></li>')
        arch = arch.replace('<li><a href="#">Legal</a></li>', '<li><a href="/terms">Legal</a></li>')
        view.with_context(lang=language).write({"arch_db": arch})

env.cr.commit()

print("BLOCK6_SUMMARY", {
    "published_products": env["product.template"].search_count([
        ("default_code", "like", "QM-%"), ("is_published", "=", True),
    ]),
    "products_with_images": env["product.template"].search_count([
        ("default_code", "like", "QM-%"), ("image_1920", "!=", False),
    ]),
    "public_categories": env["product.public.category"].search_count([]),
    "published_carriers": env["delivery.carrier"].search_count([
        ("is_published", "=", True),
    ]),
    "demo_payment": demo_provider.state if demo_provider else "missing",
    "website_language": website.default_lang_id.code,
})
