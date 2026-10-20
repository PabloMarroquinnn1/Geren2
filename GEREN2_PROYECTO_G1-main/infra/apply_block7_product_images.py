import base64
from pathlib import Path


asset_dir = Path("/mnt/extra-addons/block6_assets/product_variants")
category_files = {
    "Abarrotes": [f"abarrotes-0{i}.png" for i in range(1, 5)],
    "Bebidas": [f"bebidas-0{i}.png" for i in range(1, 5)],
    "Limpieza": [f"limpieza-0{i}.png" for i in range(1, 5)],
    "Hogar": [f"hogar-0{i}.png" for i in range(1, 5)],
    "Cuidado personal": [f"cuidado-personal-0{i}.png" for i in range(1, 5)],
    "Tecnología": [f"tecnologia-0{i}.png" for i in range(1, 5)],
}

updated = 0
for category_name, filenames in category_files.items():
    category = env["product.category"].search([("name", "=", category_name)], limit=1)
    products = env["product.template"].search([
        ("default_code", "like", "QM-%"),
        ("categ_id", "=", category.id),
    ], order="default_code")
    for index, record in enumerate(products):
        product = env["product.template"].browse(record.id)
        image_path = asset_dir / filenames[index % len(filenames)]
        product.write({"image_1920": base64.b64encode(image_path.read_bytes())})
        updated += 1
    print("CATEGORY_IMAGES", category_name, len(products), len(filenames))

env.cr.commit()
print("PRODUCT_IMAGES_UPDATED", updated)
