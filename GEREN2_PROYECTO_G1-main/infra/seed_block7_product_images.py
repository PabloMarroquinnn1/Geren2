import base64
from pathlib import Path


ASSET_DIR = Path("/mnt/extra-addons/block6_assets/product_assets")

products = env["product.template"].search([
    ("default_code", "like", "QM-%"),
    ("default_code", "!=", "QM-ENVIO"),
], order="default_code")

expected_codes = [f"QM-{index:03d}" for index in range(1, 61)]
actual_codes = products.mapped("default_code")
missing_codes = sorted(set(expected_codes) - set(actual_codes))
if missing_codes:
    raise RuntimeError(f"No se encontraron los productos: {missing_codes}")

updated = 0
for product in products:
    image_path = ASSET_DIR / f"{product.default_code}.png"
    if not image_path.exists():
        raise RuntimeError(f"Falta la imagen específica de {product.default_code}: {image_path}")
    product.write({"image_1920": base64.b64encode(image_path.read_bytes())})
    updated += 1

env.cr.commit()
print("PRODUCT_IMAGES_BY_SKU", {"updated": updated, "unique_assets": len(set(actual_codes))})
