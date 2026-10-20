"""Habilita el repositorio DMS existente y clasifica sus 15 PDF de prueba.

Ejecutar dentro de `odoo shell -d quetzalmart` en la VM. Es idempotente.
"""

root = env["dms.directory"].sudo().search(
    [("name", "=", "Documentos QuetzalMart"), ("is_root_directory", "=", True)],
    limit=1,
)
group = env["dms.access.group"].sudo().search(
    [("name", "=", "Gestión documental QuetzalMart")], limit=1
)
assert root and group, "Falta la carpeta raíz o el grupo de acceso documental"

if group not in root.group_ids:
    root.write({"group_ids": [(4, group.id)]})

categories = {
    "factura_proveedor_dms_": "Factura de proveedor",
    "contrato_outsourcing_dms_": "Contrato de outsourcing",
    "contrato_empleado_dms_": "Contrato de empleado",
}
summary = {}
for prefix, category_name in categories.items():
    category = env["dms.category"].sudo().search(
        [("name", "=", category_name)], limit=1
    )
    assert category, f"Falta la categoría {category_name}"
    files = env["dms.file"].sudo().search([("name", "like", prefix)])
    assert len(files) == 5, f"Se esperaban 5 PDF de {prefix}; hay {len(files)}"
    files.write({"category_id": category.id})
    summary[category_name] = len(files)

env.cr.commit()
print("DMS_VERIFIED", {"root": root.id, "group": group.id, "files": summary})
