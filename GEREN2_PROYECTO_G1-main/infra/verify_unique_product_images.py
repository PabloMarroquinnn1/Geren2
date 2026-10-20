import hashlib

products = env["product.template"].search([
    ("default_code", "like", "QM-%"),
    ("default_code", "!=", "QM-ENVIO"),
], order="default_code")
hashes = {}
for record in products:
    product = env["product.template"].browse(record.id)
    hashes[product.default_code] = hashlib.sha256(bytes(product.image_1920 or b"")).hexdigest()
print("IMAGE_VERIFICATION", len(hashes), len(set(hashes.values())), list(hashes.items())[:3])
