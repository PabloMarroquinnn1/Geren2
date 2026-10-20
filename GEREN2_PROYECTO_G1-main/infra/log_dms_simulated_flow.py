"""Registra el cierre del flujo académico en el chatter de cada acuerdo DMS."""

records = env['dms.file'].sudo().search([
    ('name', 'like', 'outsourcing_borrador_proveedor_')
], order='id')
assert len(records) == 5, f'Se esperaban cinco acuerdos, hay {len(records)}'
body = (
    '<p><b>Flujo académico de demostración:</b></p>'
    '<ol>'
    '<li>Preparación del modelo con datos ficticios.</li>'
    '<li>Revisión interna para la práctica.</li>'
    '<li>Aceptación representada de forma simulada; no se envió para firma y no genera consentimiento.</li>'
    '<li>Archivo en Documentos con categorías y etiquetas.</li>'
    '</ol><p>El PDF lo marca como simulación sin validez jurídica. La instalación no dispone de Odoo Sign.</p>'
)
for record in records:
    already_logged = env['mail.message'].sudo().search_count([
        ('model', '=', 'dms.file'), ('res_id', '=', record.id),
        ('body', 'ilike', 'Flujo académico de demostración'),
    ])
    if not already_logged:
        record.message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_note')
env.cr.commit()
print('DMS_FLOW_LOGGED', [(record.id, record.name) for record in records])
