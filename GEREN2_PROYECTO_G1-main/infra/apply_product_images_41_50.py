import base64
from pathlib import Path

asset_dir = Path("/mnt/extra-addons/block6_assets/product_assets")
for index in range(41, 51):
    code = f"QM-{index:03d}"
    product = env["product.template"].search([("default_code", "=", code)], limit=1)
    product.write({"image_1920": base64.b64encode((asset_dir / f"{code}.png").read_bytes())})
    env.cr.commit()
    print("UPDATED_PRODUCT_IMAGE", code)
print("BATCH_DONE", 41, 50)
