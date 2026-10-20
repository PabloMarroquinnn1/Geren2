import base64
from pathlib import Path


asset_dir = Path("/mnt/extra-addons/block6_assets/product_assets")
updated = 0
for index in range(1, 61):
    code = f"QM-{index:03d}"
    product = env["product.template"].search([("default_code", "=", code)], limit=1)
    image_path = asset_dir / f"{code}.png"
    if not product:
        raise RuntimeError(f"No existe el producto {code}")
    if not image_path.exists():
        raise RuntimeError(f"No existe la imagen {image_path}")
    product.write({"image_1920": base64.b64encode(image_path.read_bytes())})
    env.cr.commit()
    env.invalidate_all()
    updated += 1
    print("UPDATED_PRODUCT_IMAGE", code)

print("PRODUCT_IMAGES_BY_SKU", {"updated": updated, "unique_assets": updated})
