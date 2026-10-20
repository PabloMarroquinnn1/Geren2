from datetime import date


def upsert(model_name, domain, values):
    record = env[model_name].search(domain, limit=1)
    if record:
        record.write(values)
    else:
        record = env[model_name].create(values)
    return record


company = env.company
country_gt = env.ref("base.gt")
country_mx = env.ref("base.mx")
country_sv = env.ref("base.sv")
currency_gtq = env.ref("base.GTQ")

company.write({
    "name": "QuetzalMart",
    "country_id": country_gt.id,
    "currency_id": currency_gtq.id,
    "email": "info@quetzalmart.local",
    "phone": "+502 2200 2026",
})

for currency_code in ("GTQ", "USD", "MXN"):
    currency = env["res.currency"].search([("name", "=", currency_code)], limit=1)
    if currency:
        currency.active = True

spanish = env["res.lang"].search([("code", "=", "es_419")], limit=1)
admin = env.ref("base.user_admin")
admin_values = {"tz": "America/Guatemala"}
if spanish:
    admin_values["lang"] = spanish.code
admin.write(admin_values)

parameter = env["ir.config_parameter"].sudo()
parameter.set_param("web.base.url", "https://quetzalmart.34-9-149-41.sslip.io")
parameter.set_param("web.base.url.freeze", "True")

# Almacenes: se reutiliza el almacén inicial para Guatemala y se crean México y El Salvador.
warehouse_model = env["stock.warehouse"].with_company(company)
warehouse_gt = warehouse_model.search([
    ("company_id", "=", company.id), ("code", "=", "GT")
], limit=1)
if not warehouse_gt:
    warehouse_gt = warehouse_model.search([("company_id", "=", company.id)], limit=1)
warehouse_gt.write({"name": "Sucursal Guatemala", "code": "GT"})

warehouse_mx = upsert("stock.warehouse", [
    ("company_id", "=", company.id), ("code", "=", "MX")
], {"name": "Sucursal México", "code": "MX", "company_id": company.id})

warehouse_sv = upsert("stock.warehouse", [
    ("company_id", "=", company.id), ("code", "=", "SV")
], {"name": "Sucursal El Salvador", "code": "SV", "company_id": company.id})

# Departamentos y puestos.
department_names = [
    "Administración",
    "Ventas y Marketing",
    "Compras",
    "Operaciones y Logística",
    "Tecnología y Analítica",
]
departments = {
    name: upsert("hr.department", [("name", "=", name)], {
        "name": name, "company_id": company.id
    })
    for name in department_names
}

job_specs = [
    ("Gerente General", "Administración"),
    ("Analista de Compras", "Compras"),
    ("Ejecutivo de Ventas", "Ventas y Marketing"),
    ("Encargado de Bodega", "Operaciones y Logística"),
    ("Especialista de Marketing", "Ventas y Marketing"),
    ("Analista de Sistemas", "Tecnología y Analítica"),
]
jobs = {}
for job_name, department_name in job_specs:
    jobs[job_name] = upsert("hr.job", [("name", "=", job_name)], {
        "name": job_name,
        "department_id": departments[department_name].id,
        "company_id": company.id,
    })

# Empleados y contratos.
employee_names = [
    "Ana López", "Carlos Méndez", "María García", "José Hernández", "Sofía Morales",
    "Luis Ramírez", "Andrea Castillo", "Diego Pérez", "Valeria Gómez", "Jorge López",
    "Camila Herrera", "Miguel Vásquez", "Daniela Reyes", "Fernando Aguilar", "Lucía Díaz",
    "Roberto Flores", "Paola Martínez", "Alejandro Ortiz", "Natalia Rivera", "Eduardo Cruz",
    "Gabriela Sánchez", "Ricardo Alvarado", "Elena Cabrera", "Manuel Fuentes", "Isabel León",
    "Óscar Barrios", "Mónica Salazar", "Héctor Molina", "Patricia Guerra", "Samuel Rojas",
    "Claudia Pineda", "Esteban Rosales", "Verónica Chacón", "Raúl Cifuentes", "Laura Escobar",
]

for index, employee_name in enumerate(employee_names, start=1):
    job_name, department_name = job_specs[(index - 1) % len(job_specs)]
    employee = upsert("hr.employee", [("work_email", "=", f"empleado{index:02d}@quetzalmart.local")], {
        "name": employee_name,
        "work_email": f"empleado{index:02d}@quetzalmart.local",
        "work_phone": f"+502 5550 {index:04d}",
        "department_id": departments[department_name].id,
        "job_id": jobs[job_name].id,
        "company_id": company.id,
    })
    contract_values = {
        "name": f"Contrato 2026 - {employee_name}",
        "employee_id": employee.id,
        "job_id": jobs[job_name].id,
        "department_id": departments[department_name].id,
        "date_start": date(2026, 1, 5),
        "wage": 4500.0 + (index % 6) * 750.0,
        "company_id": company.id,
    }
    if "state" in env["hr.contract"]._fields:
        contract_values["state"] = "open"
    upsert("hr.contract", [("name", "=", contract_values["name"])], contract_values)

# Odoo crea un empleado y departamento de ejemplo para el administrador.
# Se archivan para conservar exactamente los conteos solicitados sin eliminar datos.
default_employee = env["hr.employee"].search([
    ("work_email", "=", "admin@example.com")
], limit=1)
if default_employee:
    default_employee.active = False
default_department = env["hr.department"].search([
    ("name", "=", "Administration")
], limit=1)
if default_department and "active" in default_department._fields:
    default_department.active = False

# Clientes y proveedores de prueba para los procesos transaccionales.
countries = [country_gt, country_mx, country_sv]
for index in range(1, 31):
    country = countries[(index - 1) % len(countries)]
    upsert("res.partner", [("ref", "=", f"CLI-{index:03d}")], {
        "name": f"Cliente QuetzalMart {index:02d}",
        "company_type": "company",
        "ref": f"CLI-{index:03d}",
        "email": f"cliente{index:02d}@example.com",
        "phone": f"+502 4400 {index:04d}",
        "street": f"Avenida Comercial {index}",
        "city": "Ciudad de Guatemala" if country == country_gt else (
            "Ciudad de México" if country == country_mx else "San Salvador"
        ),
        "country_id": country.id,
        "customer_rank": 1,
        "supplier_rank": 0,
    })

for index in range(1, 26):
    country = countries[(index - 1) % len(countries)]
    upsert("res.partner", [("ref", "=", f"PROV-{index:03d}")], {
        "name": f"Proveedor Regional {index:02d}",
        "company_type": "company",
        "ref": f"PROV-{index:03d}",
        "email": f"proveedor{index:02d}@example.com",
        "phone": f"+502 4500 {index:04d}",
        "street": f"Parque Industrial {index}",
        "city": "Ciudad de Guatemala" if country == country_gt else (
            "Monterrey" if country == country_mx else "San Salvador"
        ),
        "country_id": country.id,
        "customer_rank": 0,
        "supplier_rank": 1,
    })

# Impuestos guatemaltecos creados por l10n_gt.
sale_tax = env["account.tax"].search([
    ("company_id", "=", company.id), ("amount", "=", 12.0),
    ("type_tax_use", "=", "sale"),
], limit=1)
purchase_tax = env["account.tax"].search([
    ("company_id", "=", company.id), ("amount", "=", 12.0),
    ("type_tax_use", "=", "purchase"),
], limit=1)

# Catálogo de 60 productos publicables.
catalog = {
    "Abarrotes": [
        "Arroz premium 1 kg", "Frijol negro 1 kg", "Azúcar blanca 1 kg", "Harina de maíz 1 kg",
        "Pasta espagueti 400 g", "Aceite vegetal 900 ml", "Atún en agua 140 g", "Cereal de maíz 500 g",
        "Café guatemalteco 340 g", "Sal yodada 1 kg",
    ],
    "Bebidas": [
        "Agua pura 600 ml", "Agua pura 1.5 L", "Jugo de naranja 1 L", "Jugo de manzana 1 L",
        "Bebida gaseosa cola 2 L", "Bebida gaseosa limón 2 L", "Té frío durazno 500 ml",
        "Bebida energética 473 ml", "Leche entera 1 L", "Leche deslactosada 1 L",
    ],
    "Limpieza": [
        "Detergente en polvo 1 kg", "Jabón lavatrastos 750 ml", "Desinfectante lavanda 1 L",
        "Limpiavidrios 500 ml", "Cloro 1 galón", "Suavizante de ropa 850 ml",
        "Esponjas multiuso paquete", "Bolsas para basura grandes", "Toallas de papel paquete",
        "Limpiador de pisos 1 L",
    ],
    "Hogar": [
        "Juego de recipientes herméticos", "Sartén antiadherente 24 cm", "Olla de acero 3 L",
        "Vaso térmico 500 ml", "Juego de cubiertos 24 piezas", "Almohada estándar",
        "Juego de sábanas matrimonial", "Organizador plástico grande", "Bombillo LED 12 W",
        "Extensión eléctrica 3 m",
    ],
    "Cuidado personal": [
        "Shampoo hidratante 750 ml", "Acondicionador 750 ml", "Jabón corporal paquete de 3",
        "Pasta dental 150 ml", "Cepillo dental medio", "Desodorante aerosol 150 ml",
        "Crema corporal 400 ml", "Papel higiénico paquete de 12", "Protector solar FPS 50",
        "Gel antibacterial 500 ml",
    ],
    "Tecnología": [
        "Audífonos inalámbricos", "Cargador USB-C 20 W", "Cable USB-C 1 m", "Memoria USB 64 GB",
        "Teclado inalámbrico", "Mouse óptico", "Bocina Bluetooth", "Soporte para laptop",
        "Cámara web Full HD", "Regleta protectora de voltaje",
    ],
}

all_category = env.ref("product.product_category_all")
product_index = 0
product_records = []
public_categories = {}

for category_index, (category_name, product_names) in enumerate(catalog.items(), start=1):
    category = upsert("product.category", [("name", "=", category_name)], {
        "name": category_name,
        "parent_id": all_category.id,
    })
    public_category = upsert("product.public.category", [("name", "=", category_name)], {
        "name": category_name,
    })
    public_categories[category_name] = public_category

    for local_index, product_name in enumerate(product_names, start=1):
        product_index += 1
        sku = f"QM-{product_index:03d}"
        cost = round(4.0 + product_index * 2.35 + category_index * 3.0, 2)
        price = round(cost * 1.45, 2)
        values = {
            "name": product_name,
            "default_code": sku,
            "barcode": f"7400000{product_index:06d}",
            "list_price": price,
            "standard_price": cost,
            "categ_id": category.id,
            "sale_ok": True,
            "purchase_ok": True,
            "is_published": True,
            "description_sale": f"Producto QuetzalMart: {product_name}.",
            "weight": round(0.2 + (product_index % 10) * 0.15, 2),
            "public_categ_ids": [(6, 0, [public_category.id])],
        }
        if "is_storable" in env["product.template"]._fields:
            values["is_storable"] = True
        else:
            values["type"] = "product"
        if sale_tax:
            values["taxes_id"] = [(6, 0, [sale_tax.id])]
        if purchase_tax:
            values["supplier_taxes_id"] = [(6, 0, [purchase_tax.id])]
        template = upsert("product.template", [("default_code", "=", sku)], values)
        product_records.append(template.product_variant_id)

# Existencias iniciales en las tres sucursales.
quant_model = env["stock.quant"]
warehouse_targets = [(warehouse_gt, 80.0), (warehouse_mx, 55.0), (warehouse_sv, 45.0)]
for product in product_records:
    for warehouse, target_quantity in warehouse_targets:
        location = warehouse.lot_stock_id
        current_quantity = sum(quant_model.search([
            ("product_id", "=", product.id), ("location_id", "=", location.id)
        ]).mapped("quantity"))
        difference = target_quantity - current_quantity
        if difference:
            quant_model._update_available_quantity(product, location, difference)

# Estructura de gestión documental.
storage = upsert("dms.storage", [("name", "=", "Documentos QuetzalMart")], {
    "name": "Documentos QuetzalMart",
    "save_type": "database",
    "company_id": company.id,
})
root_directory = env["dms.directory"].search([
    ("storage_id", "=", storage.id), ("is_root_directory", "=", True)
], limit=1)
if not root_directory:
    root_directory = env["dms.directory"].create({
        "name": "Documentos QuetzalMart",
        "storage_id": storage.id,
        "is_root_directory": True,
        "company_id": company.id,
    })

for directory_name in (
    "Facturas de proveedores", "Contratos de outsourcing", "Contratos de empleados"
):
    upsert("dms.directory", [
        ("name", "=", directory_name), ("parent_id", "=", root_directory.id)
    ], {
        "name": directory_name,
        "storage_id": storage.id,
        "parent_id": root_directory.id,
        "company_id": company.id,
    })

for category_name in (
    "Factura de proveedor", "Contrato de outsourcing", "Contrato de empleado"
):
    upsert("dms.category", [("name", "=", category_name)], {"name": category_name})

for color, tag_name in enumerate(("Proveedor", "Outsourcing", "Empleado", "Legal", "2026"), start=1):
    values = {"name": tag_name}
    if "color" in env["dms.tag"]._fields:
        values["color"] = color
    upsert("dms.tag", [("name", "=", tag_name)], values)

# Sitio web, lista de marketing y proveedor de pago de demostración.
website = env["website"].search([], limit=1)
if website:
    website.write({
        "name": "QuetzalMart",
        "domain": "https://quetzalmart.34-9-149-41.sslip.io",
        "company_id": company.id,
    })

upsert("mailing.list", [("name", "=", "Clientes QuetzalMart")], {
    "name": "Clientes QuetzalMart",
    "is_public": False,
})

demo_provider = env["payment.provider"].search([("code", "=", "demo")], limit=1)
if demo_provider:
    demo_provider.write({"state": "test", "company_id": company.id})

env.cr.commit()

print("BLOCK4_SUMMARY", {
    "warehouses": env["stock.warehouse"].search_count([("company_id", "=", company.id)]),
    "departments": env["hr.department"].search_count([]),
    "jobs": env["hr.job"].search_count([]),
    "employees": env["hr.employee"].search_count([]),
    "contracts": env["hr.contract"].search_count([]),
    "customers": env["res.partner"].search_count([("customer_rank", ">", 0)]),
    "suppliers": env["res.partner"].search_count([("supplier_rank", ">", 0)]),
    "products": env["product.template"].search_count([("default_code", "like", "QM-")]),
    "dms_directories": env["dms.directory"].search_count([]),
})
