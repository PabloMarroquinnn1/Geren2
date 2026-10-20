field = env["product.template"]._fields["image_1920"]
print("FIELD", type(field).__name__, getattr(field, "related", None), getattr(field, "compute", None), getattr(field, "inverse", None), getattr(field, "store", None))
variant_field = env["product.product"]._fields["image_1920"]
print("VARIANT_FIELD", type(variant_field).__name__, getattr(variant_field, "related", None), getattr(variant_field, "compute", None), getattr(variant_field, "inverse", None), getattr(variant_field, "store", None))
