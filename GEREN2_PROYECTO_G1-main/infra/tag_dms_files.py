"""Etiqueta los 15 documentos del sistema documental según el enunciado."""

env = env  # noqa: F821 - proporcionado por odoo shell
Tag = env["dms.tag"]
File = env["dms.file"]

groups = {
    "factura_proveedor_dms_": "Proveedor",
    "contrato_outsourcing_dms_": "Outsourcing",
    "contrato_empleado_dms_": "Empleado",
}
year_tag = Tag.search([("name", "=", "2026")], limit=1)
if not year_tag:
    year_tag = Tag.create({"name": "2026"})

summary = {}
for prefix, tag_name in groups.items():
    tag = Tag.search([("name", "=", tag_name)], limit=1)
    if not tag:
        tag = Tag.create({"name": tag_name})
    files = File.search([("name", "like", prefix)])
    for record in files:
        record.write({"tag_ids": [(6, 0, [tag.id, year_tag.id])]})
    summary[tag_name] = len(files)

env.cr.commit()
print({"tagged_files": summary, "year_tag": year_tag.id})
