import base64
import mimetypes
from pathlib import Path

base = Path('/tmp/dms_uploads_new')
mapping = {}
for filename in sorted(base.glob('factura_proveedor_dms_*.pdf')):
    mapping[filename] = 2
for filename in sorted(base.glob('contrato_outsourcing_dms_*.pdf')):
    mapping[filename] = 3
for filename in sorted(base.glob('contrato_empleado_dms_*.pdf')):
    mapping[filename] = 4

File = env['dms.file'].sudo()
created = []
skipped = []
for path, directory_id in mapping.items():
    existing = File.search([('name', '=', path.name), ('directory_id', '=', directory_id)], limit=1)
    if existing:
        skipped.append(path.name)
        continue
    data = path.read_bytes()
    vals = {
        'name': path.name,
        'directory_id': directory_id,
        'content': base64.b64encode(data),
        'mimetype': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
    }
    record = File.create(vals)
    created.append((record.id, record.name, record.directory_id.id, len(data)))
env.cr.commit()
print('CREATED', len(created))
for row in created:
    print('FILE', row)
print('SKIPPED', len(skipped))
print('TOTAL_DMS_FILES', File.search_count([]))
