import base64
from pathlib import Path
import hashlib

products = [
    ("QM-001", "abarrotes-01.png"),
    ("QM-002", "abarrotes-02.png"),
    ("QM-003", "abarrotes-03.png"),
]
before = {}
for code, filename in products:
    product = env["product.template"].search([("default_code", "=", code)], limit=1)
    before[code] = hashlib.sha256(bytes(product.image_1920 or b"")).hexdigest()[:10]
    path = Path("/mnt/extra-addons/block6_assets/product_variants") / filename
    product.write({"image_1920": base64.b64encode(path.read_bytes())})
env.cr.commit()
after = {}
for code, _filename in products:
    product = env["product.template"].search([("default_code", "=", code)], limit=1)
    after[code] = hashlib.sha256(bytes(product.image_1920 or b"")).hexdigest()[:10]
print("ONE_PRODUCT_IMAGE", before, after)
