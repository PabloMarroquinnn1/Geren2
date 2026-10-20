"""Renueva los PDF DMS y registra documentos académicos trazables en Odoo."""

import base64
import html
from io import BytesIO
from pathlib import Path
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)


out_dir = Path('/tmp/dms_verified')
out_dir.mkdir(parents=True, exist_ok=True)
File = env['dms.file'].sudo()
Tag = env['dms.tag'].sudo()
year_tag = Tag.search([('name', '=', '2026')], limit=1)
assert year_tag, 'Falta etiqueta 2026'
demo_tag = Tag.search([('name', '=', 'Simulación académica')], limit=1)
if not demo_tag:
    demo_tag = Tag.create({'name': 'Simulación académica'})
flow_tag = Tag.search([('name', '=', 'Flujo demo completado')], limit=1)
if not flow_tag:
    flow_tag = Tag.create({'name': 'Flujo demo completado'})

GREEN = colors.HexColor('#087F5B')
GREEN_DARK = colors.HexColor('#075B45')
GREEN_PALE = colors.HexColor('#E7F5EF')
ORANGE = colors.HexColor('#F08C2E')
ORANGE_PALE = colors.HexColor('#FFF3E6')
INK = colors.HexColor('#24323D')
MUTED = colors.HexColor('#64727C')
LINE = colors.HexColor('#DCE5E1')
WHITE = colors.white
PAGE_W, PAGE_H = A4
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Brand', parent=styles['Normal'], fontName='Helvetica-Bold',
    fontSize=10, leading=12, textColor=WHITE, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='HeroTitle', parent=styles['Title'], fontName='Helvetica-Bold',
    fontSize=20, leading=24, textColor=GREEN_DARK, alignment=TA_LEFT, spaceAfter=4))
styles.add(ParagraphStyle(name='Subhead', parent=styles['Normal'], fontSize=9,
    leading=13, textColor=MUTED, spaceAfter=9))
styles.add(ParagraphStyle(name='SectionGreen', parent=styles['Heading2'], fontName='Helvetica-Bold',
    fontSize=10.5, leading=12, textColor=GREEN_DARK, spaceBefore=7, spaceAfter=3,
    keepWithNext=True))
styles.add(ParagraphStyle(name='BodyClean', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=9, leading=13, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name='SmallMuted', parent=styles['Normal'], fontName='Helvetica',
    fontSize=7.5, leading=10, textColor=MUTED))
styles.add(ParagraphStyle(name='Notice', parent=styles['Normal'], fontName='Helvetica-Bold',
    fontSize=8.2, leading=11, textColor=GREEN_DARK, alignment=TA_CENTER))


def safe(value):
    return html.escape(str(value if value not in (None, False) else '-'))


def page_chrome(pdf, doc):
    pdf.saveState()
    pdf.setFillColor(GREEN_DARK)
    pdf.rect(0, PAGE_H - 14*mm, PAGE_W, 14*mm, stroke=0, fill=1)
    pdf.setFillColor(ORANGE)
    pdf.rect(0, PAGE_H - 15.5*mm, PAGE_W, 1.5*mm, stroke=0, fill=1)
    pdf.setFillColor(WHITE)
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(18*mm, PAGE_H - 9.5*mm, 'QUETZALMART')
    pdf.setFont('Helvetica', 8)
    pdf.drawRightString(PAGE_W - 18*mm, PAGE_H - 9.5*mm, 'GESTIÓN DOCUMENTAL · 2026')
    pdf.setStrokeColor(LINE)
    pdf.line(18*mm, 15*mm, PAGE_W - 18*mm, 15*mm)
    pdf.setFillColor(MUTED)
    pdf.setFont('Helvetica', 7.5)
    pdf.drawString(18*mm, 10*mm, 'SIMULACIÓN ACADÉMICA · SIN VALIDEZ JURÍDICA')
    pdf.drawRightString(PAGE_W - 18*mm, 10*mm, f'Página {doc.page}')
    pdf.restoreState()


def styled_agreement(title, doc_code, party_rows, sections, signatories, status):
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=21*mm, bottomMargin=21*mm,
                            title=title, author='QuetzalMart · Simulación académica')
    story = []
    badge = Table([[Paragraph('ACUERDO DE DEMOSTRACIÓN', styles['Brand'])]], colWidths=[59*mm])
    badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ORANGE), ('BOX', (0,0), (-1,-1), 0, ORANGE),
        ('LEFTPADDING', (0,0), (-1,-1), 8), ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.extend([Spacer(1, 3*mm), badge, Spacer(1, 4*mm),
                  Paragraph(safe(title), styles['HeroTitle']),
                  Paragraph(f'Código <b>{safe(doc_code)}</b> &nbsp; · &nbsp; Fecha de emisión: 29/09/2026',
                            styles['Subhead'])])
    notice = Table([[Paragraph('SIMULACIÓN ACADÉMICA · DATOS FICTICIOS · NO SUSCRITO · SIN VALIDEZ JURÍDICA',
                               styles['Notice'])]], colWidths=[PAGE_W - 36*mm])
    notice.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GREEN_PALE), ('BOX', (0,0), (-1,-1), .7, GREEN),
        ('LEFTPADDING', (0,0), (-1,-1), 9), ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.extend([notice, Spacer(1, 5*mm), Paragraph('PARTES Y DATOS DEL ACUERDO', styles['SectionGreen'])])
    party_table = Table([[Paragraph(f'<b>{safe(k)}</b>', styles['BodyClean']),
                          Paragraph(safe(v), styles['BodyClean'])] for k,v in party_rows],
                        colWidths=[48*mm, PAGE_W - 84*mm])
    party_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), GREEN_PALE), ('GRID', (0,0), (-1,-1), .4, LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7), ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(party_table)
    for heading, paragraphs in sections:
        blocks = [Paragraph(safe(heading), styles['SectionGreen'])]
        for paragraph in paragraphs:
            blocks.append(Paragraph(safe(paragraph), styles['BodyClean']))
        story.append(KeepTogether(blocks))
    story.append(Paragraph('REGISTRO DEL FLUJO DEMOSTRATIVO', styles['SectionGreen']))
    flow = [
        ['Preparación', 'Documento modelo creado con datos ficticios.'],
        ['Revisión', 'Revisado para la demostración académica.'],
        ['Aceptación', 'Aceptación simulada; no representa firma ni consentimiento real.'],
        ['Archivo', 'Clasificado y archivado en Documentos de Odoo.'],
    ]
    ft = Table([[Paragraph(f'<b>{safe(a)}</b>', styles['SmallMuted']),
                 Paragraph(safe(b), styles['SmallMuted'])] for a,b in flow],
               colWidths=[33*mm, PAGE_W - 69*mm])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), ORANGE_PALE), ('GRID', (0,0), (-1,-1), .4, LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7), ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.extend([ft, Spacer(1, 6*mm)])
    sig = Table([[Paragraph(f'<b>{safe(signatories[0])}</b><br/><br/>Firma ilustrativa: DEMO<br/>Sin validez jurídica', styles['BodyClean']),
                  Paragraph(f'<b>{safe(signatories[1])}</b><br/><br/>Firma ilustrativa: DEMO<br/>Sin validez jurídica', styles['BodyClean'])]],
                colWidths=[(PAGE_W-40*mm)/2]*2, rowHeights=[23*mm])
    sig.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), .8, ORANGE), ('INNERGRID', (0,0), (-1,-1), .5, LINE),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFCF7')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.extend([sig, Spacer(1, 3*mm), Paragraph(safe(status), styles['SmallMuted'])])
    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    return stream.getvalue()


def update_sample(prefix, index, name, pdf_bytes, model, record_id, tag_name):
    assert pdf_bytes.startswith(b'%PDF-') and len(pdf_bytes) > 1000
    sample = File.search([('name', '=', f'{prefix}{index:03d}.pdf')], limit=1)
    if not sample:
        sample = File.search([('name', '=', name)], limit=1)
    assert sample, f'No existe muestra {prefix}{index:03d}'
    tag = Tag.search([('name', '=', tag_name)], limit=1)
    assert tag, f'Falta etiqueta {tag_name}'
    sample.write({
        'name': name,
        'content': base64.b64encode(pdf_bytes).decode('ascii'),
        'res_model': model,
        'res_id': record_id,
        'tag_ids': [(6, 0, [tag.id, year_tag.id, demo_tag.id, flow_tag.id])],
    })
    assert sample.size > 1000 and sample.mimetype == 'application/pdf'
    (out_dir / name).write_bytes(pdf_bytes)
    return sample.id


bills = env['account.move'].sudo().search([
    ('move_type', '=', 'in_invoice'), ('state', '=', 'posted')
], order='id', limit=5)
contracts = env['hr.contract'].sudo().search([], order='id', limit=5)
suppliers = env['res.partner'].sudo().search([
    ('supplier_rank', '>', 0), ('name', '!=', False)
], order='id', limit=5)
assert len(bills) == len(contracts) == len(suppliers) == 5

results = {'facturas_contabilizadas': [], 'extractos_contrato_empleado': [],
           'borradores_outsourcing_sin_aceptacion': []}
report = env['ir.actions.report'].sudo()
for index, bill in enumerate(bills, 1):
    pdf_bytes, _ = report._render_qweb_pdf('account.account_invoices', res_ids=[bill.id])
    name = f'factura_proveedor_registro_{bill.id}.pdf'
    file_id = update_sample('factura_proveedor_dms_', index, name, pdf_bytes,
                            'account.move', bill.id, 'Proveedor')
    results['facturas_contabilizadas'].append((file_id, bill.name))

for index, contract in enumerate(contracts, 1):
    employee = contract.employee_id
    code = f'RH-DEMO-{contract.id:03d}'
    end_date = contract.date_end or 'No definida en el registro Odoo'
    sections = [
        ('1. Funciones y puesto', [
            f'Para esta simulación académica, {employee.name} ocupa el puesto de {contract.job_id.name or "puesto registrado"} en el departamento {contract.department_id.name or "área registrada"}.',
            'Las funciones ilustrativas incluyen ejecutar las tareas del puesto, atender procesos internos y resguardar los recursos asignados. El alcance detallado se considera material de demostración.'
        ]),
        ('2. Vigencia y condiciones económicas', [
            f'Inicio registrado: {contract.date_start or "No definido"}. Fecha final registrada: {end_date}. Estado actual en Odoo: {contract.state}.',
            f'Remuneración base registrada en Odoo: {contract.wage:,.2f} GTQ. Este documento reproduce el dato del sistema únicamente para la práctica.'
        ]),
        ('3. Confidencialidad y recursos', [
            'El modelo plantea el resguardo de la información y el uso responsable de los recursos de QuetzalMart. Estas cláusulas son ilustrativas y requieren revisión antes de cualquier uso real.'
        ]),
    ]
    pdf_bytes = styled_agreement('Acuerdo laboral simulado', code, [
        ('Empleador', 'QuetzalMart · empresa de demostración'),
        ('Persona empleada', employee.name),
        ('Puesto', contract.job_id.name or '-'),
        ('Departamento', contract.department_id.name or '-'),
        ('Registro de origen', f'hr.contract / {contract.id}'),
    ], sections, ['QuetzalMart · representante ficticio', f'{employee.name} · participante ficticio'],
        'Aceptación representada solo como demostración. No existe firma electrónica o manuscrita válida.')
    name = f'contrato_empleado_registro_{contract.id:03d}.pdf'
    file_id = update_sample('contrato_empleado_dms_', index, name, pdf_bytes,
                            'hr.contract', contract.id, 'Empleado')
    results['extractos_contrato_empleado'].append((file_id, contract.name))

service_specs = [
    ('Distribución local', 'Programación de rutas y coordinación de entregas en Guatemala.', 5800),
    ('Soporte tecnológico', 'Atención de incidencias básicas y mantenimiento preventivo de equipos.', 4500),
    ('Limpieza de instalaciones', 'Rutina de limpieza de áreas comunes y reporte de incidencias.', 3200),
    ('Seguridad de instalaciones', 'Control de acceso y bitácora de novedades para el sitio de demostración.', 8500),
    ('Gestión de residuos', 'Recolección programada y registro de retiros de residuos no peligrosos.', 1900),
]
for index, supplier in enumerate(suppliers, 1):
    service, scope, monthly_fee = service_specs[index-1]
    contract_start = date(2026, 10, 1)
    contract_end = date(2027, 9, 30)
    code = f'OUT-DEMO-{index:03d}'
    sections = [
        ('1. Objeto y alcance', [
            f'Servicio de {service.lower()}: {scope} Alcance, horarios y niveles de servicio son supuestos académicos no negociados.'
        ]),
        ('2. Plazo de referencia', [
            f'Periodo de ejemplo: {contract_start.strftime("%d/%m/%Y")} al {contract_end.strftime("%d/%m/%Y")}; las fechas son ficticias y no generan compromiso.'
        ]),
        ('3. Precio y pago de referencia', [
            f'Tarifa de ejemplo: Q {monthly_fee:,.2f} mensuales, más impuestos aplicables. Pago ilustrativo contra factura y revisión del servicio; no implica obligación real.'
        ]),
        ('4. Responsabilidades, confidencialidad y cambios', [
            'El proveedor documentaría entregas e incidentes; QuetzalMart revisaría resultados. Ambas partes protegerían información y autorizarían por escrito cualquier cambio. Cláusula ilustrativa.'
        ]),
    ]
    pdf_bytes = styled_agreement(f'Acuerdo simulado de {service.lower()}', code, [
        ('Empresa solicitante', 'QuetzalMart · empresa de demostración'),
        ('Proveedor propuesto', supplier.name + ' · proveedor ficticio'),
        ('Servicio', service),
        ('Plazo de referencia', f'{contract_start} a {contract_end}'),
        ('Tarifa ilustrativa', f'Q {monthly_fee:,.2f} por mes'),
        ('Registro de origen', f'res.partner / {supplier.id}'),
    ], sections, ['QuetzalMart · representante ficticio', supplier.name + ' · proveedor ficticio'],
        'Aceptación representada solo como demostración. No existe firma electrónica o manuscrita válida.')
    name = f'outsourcing_borrador_proveedor_{supplier.id:03d}.pdf'
    file_id = update_sample('contrato_outsourcing_dms_', index, name, pdf_bytes,
                            'res.partner', supplier.id, 'Outsourcing')
    results['borradores_outsourcing_sin_aceptacion'].append((file_id, supplier.name))

env.cr.commit()
print('DMS_RECORD_DOCUMENTS', results)
