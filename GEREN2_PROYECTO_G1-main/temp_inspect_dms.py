print('DIRECTORY_FIELDS', sorted(env['dms.directory']._fields.keys()))
for d in env['dms.directory'].sudo().search([]):
    print('DIR', d.id, d.name, d.read(['name','res_model','res_id']))
print('FILE_FIELDS', sorted(env['dms.file']._fields.keys()))
for f in env['dms.file'].sudo().search([]):
    print('FILE', f.id, f.name, f.directory_id.id)
env.cr.commit()
