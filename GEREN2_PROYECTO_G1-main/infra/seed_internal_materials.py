import base64
import hashlib
import json
from pathlib import Path


BASE_DIR = Path("/tmp/quetzalmart-materiales-operativos")
MANIFEST = BASE_DIR / "datos" / "materiales_operativos_60.json"
ASSET_DIR = BASE_DIR / "assets"
EXPECTED_CODES = {f"QMI-{index:03d}" for index in range(1, 61)}


def upsert(model_name, domain, values):
    model = env[model_name]
    record = model.search(domain, limit=1)
    if record:
        record.write(values)
        return record
    return model.create(values)


items = json.loads(MANIFEST.read_text(encoding="utf-8"))
actual_codes = {item["code"] for item in items}
if len(items) != 60 or actual_codes != EXPECTED_CODES:
    raise RuntimeError("El manifiesto no contiene los 60 códigos QMI esperados.")
source_image_hashes = {
    hashlib.sha256((ASSET_DIR / f'{item["code"]}.png').read_bytes()).hexdigest()
    for item in items
}
if len(source_image_hashes) != 60:
    raise RuntimeError("Las imágenes fuente de los materiales no son todas distintas.")

company = env.company
warehouse_model = env["stock.warehouse"].with_company(company)
warehouses = warehouse_model.search([
    ("company_id", "=", company.id), ("code", "in", ["GT", "MX", "SV"])
])
warehouse_by_code = {warehouse.code: warehouse for warehouse in warehouses}
if set(warehouse_by_code) != {"GT", "MX", "SV"}:
    raise RuntimeError("Se requieren los almacenes GT, MX y SV para asignar existencias.")

all_category = env.ref("product.product_category_all")
root_category = upsert("product.category", [
    ("name", "=", "Materiales y suministros internos"),
    ("parent_id", "=", all_category.id),
], {
    "name": "Materiales y suministros internos",
    "parent_id": all_category.id,
})

category_records = {}
for category_name in sorted({item["category"] for item in items}):
    category_records[category_name] = upsert("product.category", [
        ("name", "=", category_name), ("parent_id", "=", root_category.id),
    ], {"name": category_name, "parent_id": root_category.id})

product_model = env["product.template"].with_company(company)
variant_model = env["product.product"].with_company(company)
quant_model = env["stock.quant"].with_company(company)
created_or_updated = 0

for item in items:
    image_path = ASSET_DIR / f'{item["code"]}.png'
    if not image_path.is_file():
        raise FileNotFoundError(f"Falta la imagen individual {image_path}")

    values = {
        "name": item["name"],
        "default_code": item["code"],
        "categ_id": category_records[item["category"]].id,
        "sale_ok": False,
        "purchase_ok": True,
        "list_price": 0.0,
        "standard_price": float(item["cost"]),
        "is_published": False,
        "image_1920": base64.b64encode(image_path.read_bytes()),
        "description_sale": "Material de uso interno para las sucursales; no es un artículo vendible.",
        "description_purchase": f"Material operativo QuetzalMart: {item['name']}. Uso interno en sucursales.",
        "public_categ_ids": [(6, 0, [])],
    }
    product_fields = product_model._fields
    if "is_storable" in product_fields:
        values["is_storable"] = True
    else:
        values["type"] = "product"
    if "available_in_pos" in product_fields:
        values["available_in_pos"] = False

    template = product_model.search([("default_code", "=", item["code"])], limit=1)
    if template:
        template.write(values)
    else:
        template = product_model.create(values)
    created_or_updated += 1
    product = variant_model.browse(template.product_variant_id.id)

    # Mantiene una cantidad operativa en cada sucursal; al reejecutar ajusta solo la diferencia.
    for warehouse in warehouse_by_code.values():
        location = warehouse.lot_stock_id
        current_quantity = sum(quant_model.search([
            ("product_id", "=", product.id), ("location_id", "=", location.id)
        ]).mapped("quantity"))
        target_quantity = float(item["qty_per_branch"])
        difference = target_quantity - current_quantity
        if difference:
            quant_model._update_available_quantity(product, location, difference)

materials = product_model.search([("default_code", "like", "QMI-%")])
if len(materials) != 60:
    raise RuntimeError(f"Validación fallida: se encontraron {len(materials)} materiales QMI.")
if materials.filtered(lambda record: record.is_published or record.sale_ok):
    raise RuntimeError("Validación fallida: algún material QMI está publicado o marcado vendible.")
if materials.filtered(lambda record: not record.image_1920):
    raise RuntimeError("Validación fallida: algún material QMI no tiene imagen.")
stored_image_hashes = {
    hashlib.sha256(record.image_1920).hexdigest()
    for record in materials
}
if len(stored_image_hashes) != 60:
    raise RuntimeError("Validación fallida: las imágenes guardadas no son todas distintas.")

branch_summary = {}
for code, warehouse in sorted(warehouse_by_code.items()):
    products_with_stock = 0
    units = 0.0
    for template in materials:
        product = template.product_variant_id
        quantity = sum(quant_model.search([
            ("product_id", "=", product.id),
            ("location_id", "=", warehouse.lot_stock_id.id),
        ]).mapped("quantity"))
        if quantity > 0:
            products_with_stock += 1
            units += quantity
    branch_summary[code] = {
        "warehouse": warehouse.name,
        "materials_with_stock": products_with_stock,
        "units": units,
    }
    if products_with_stock != 60:
        raise RuntimeError(f"Validación fallida: {warehouse.name} tiene {products_with_stock}/60 materiales.")

env.cr.execute("""
    SELECT COUNT(*) AS materiales,
           COUNT(*) FILTER (WHERE NOT pt.sale_ok) AS no_vendibles,
           COUNT(*) FILTER (WHERE NOT pt.is_published) AS no_publicados,
           COUNT(*) FILTER (WHERE EXISTS (
               SELECT 1 FROM ir_attachment ia
               WHERE ia.res_model = 'product.template'
                 AND ia.res_id = pt.id
                 AND ia.res_field = 'image_1920'
           )) AS con_imagen
    FROM product_product pp
    JOIN product_template pt ON pt.id = pp.product_tmpl_id
    WHERE pp.default_code LIKE 'QMI-%'
""")
sql_counts = env.cr.dictfetchone()
if sql_counts != {
    "materiales": 60,
    "no_vendibles": 60,
    "no_publicados": 60,
    "con_imagen": 60,
}:
    raise RuntimeError(f"Validación SQL fallida para los materiales QMI: {sql_counts}")

env.cr.execute("""
    SELECT sw.name AS sucursal,
           COUNT(DISTINCT pp.id) AS materiales_con_existencia,
           ROUND(COALESCE(SUM(sq.quantity), 0)::numeric, 2) AS unidades_internas
    FROM stock_warehouse sw
    JOIN stock_quant sq ON sq.location_id = sw.lot_stock_id
    JOIN product_product pp ON pp.id = sq.product_id
    WHERE sw.code IN ('GT', 'MX', 'SV')
      AND pp.default_code LIKE 'QMI-%'
      AND sq.quantity > 0
    GROUP BY sw.id, sw.name
    ORDER BY sw.code
""")
sql_branch_summary = env.cr.dictfetchall()
if len(sql_branch_summary) != 3 or any(row["materiales_con_existencia"] != 60 for row in sql_branch_summary):
    raise RuntimeError(f"Validación SQL por sucursal fallida: {sql_branch_summary}")

env.cr.execute("""
    SELECT pp.default_code,
           COALESCE(pt.name ->> 'es_GT', pt.name ->> 'en_US', '') AS material,
           pc.name AS categoria,
           pp.standard_price AS costo,
           pt.sale_ok AS vendible,
           pt.is_published AS publicado,
           EXISTS (
               SELECT 1 FROM ir_attachment ia
               WHERE ia.res_model = 'product.template'
                 AND ia.res_id = pt.id
                 AND ia.res_field = 'image_1920'
           ) AS tiene_imagen
    FROM product_product pp
    JOIN product_template pt ON pt.id = pp.product_tmpl_id
    LEFT JOIN product_category pc ON pc.id = pt.categ_id
    WHERE pp.default_code LIKE 'QMI-%'
    ORDER BY pp.default_code
""")
sql_detail_rows = env.cr.fetchall()
if len(sql_detail_rows) != 60:
    raise RuntimeError(f"Validación SQL del listado detallado fallida: {len(sql_detail_rows)} registros.")

env.cr.commit()

print("INTERNAL_MATERIALS_SUMMARY", {
    "created_or_updated": created_or_updated,
    "materials": len(materials),
    "unpublished": len(materials.filtered(lambda record: not record.is_published)),
    "not_for_sale": len(materials.filtered(lambda record: not record.sale_ok)),
    "with_unique_images": len(stored_image_hashes),
    "branches": branch_summary,
})
print("INTERNAL_MATERIALS_SQL_COUNTS", sql_counts)
print("INTERNAL_MATERIALS_SQL_BRANCHES", sql_branch_summary)
print("INTERNAL_MATERIALS_SQL_DETAIL_ROWS", len(sql_detail_rows))
