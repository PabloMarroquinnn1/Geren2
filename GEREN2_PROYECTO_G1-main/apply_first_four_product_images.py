import base64
from pathlib import Path

asset_dir = Path("/mnt/extra-addons/block6_assets/product_variants")
categories = [
    ("abarrotes", 1),
    ("bebidas", 11),
    ("limpieza", 21),
    ("hogar", 31),
    ("cuidado-personal", 41),
    ("tecnologia", 51),
]

for prefix, start in categories:
    for offset in range(4):
        code = f"QM-{start + offset:03d}"
        product = env["product.template"].search([("default_code", "=", code)], limit=1)
        filename = f"{prefix}-0{offset + 1}.png"
        product.write({"image_1920": base64.b64encode((asset_dir / filename).read_bytes())})
        print("UPDATED", code, filename)

env.cr.commit()
print("FIRST_FOUR_DONE")
