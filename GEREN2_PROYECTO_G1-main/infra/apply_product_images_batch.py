import base64
import os
from pathlib import Path


asset_dir = Path("/mnt/extra-addons/block6_assets/product_assets")
start = int(os.environ.get("BATCH_START", "1"))
end = min(start + 10, 61)
updated = 0
for index in range(start, end):
    code = f"QM-{index:03d}"
    product = env["product.template"].search([("default_code", "=", code)], limit=1)
    image_path = asset_dir / f"{code}.png"
    if not product or not image_path.exists():
        raise RuntimeError(f"Falta {code} o su imagen")
    product.write({"image_1920": base64.b64encode(image_path.read_bytes())})
    env.cr.commit()
    env.invalidate_all()
    updated += 1
    print("UPDATED_PRODUCT_IMAGE", code)
print("BATCH_DONE", start, end - 1, updated)
