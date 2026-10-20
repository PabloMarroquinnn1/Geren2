import hashlib

for category_name in ("Abarrotes", "Bebidas", "Limpieza", "Hogar", "Cuidado personal", "Tecnología"):
    category = env["product.category"].search([("name", "=", category_name)], limit=1)
    records = env["product.template"].search([
        ("default_code", "like", "QM-%"),
        ("categ_id", "=", category.id),
    ], order="default_code")
    products = [env["product.template"].browse(record.id) for record in records]
    images = [bytes(product.image_1920 or b"") for product in products]
    hashes = [hashlib.sha256(image).hexdigest()[:10] for image in images]
    print(category_name, len(products), len(set(hashes)), hashes[:6])
