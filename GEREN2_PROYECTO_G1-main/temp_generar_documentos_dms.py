from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "dms_documentos_prueba"
OUT.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
title = ParagraphStyle("Title", parent=styles["Title"], alignment=TA_CENTER, fontSize=16, leading=20)
body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=14)

def make_pdf(path: Path, heading: str, subtitle: str, rows: list[tuple[str, str]], paragraphs: list[str]) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [Paragraph("QuetzalMart", title), Spacer(1, 12), Paragraph(heading, title), Spacer(1, 8), Paragraph(subtitle, body), Spacer(1, 18)]
    table = Table([[Paragraph(f"<b>{k}</b>", body), Paragraph(v, body)] for k, v in rows], colWidths=[150, 330])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eeeeee")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 18))
    for paragraph in paragraphs:
        story.append(Paragraph(paragraph, body))
        story.append(Spacer(1, 10))
    doc.build(story)

for i in range(1, 6):
    make_pdf(
        OUT / f"factura_proveedor_dms_{i:03d}.pdf",
        f"Factura de proveedor DMS {i:03d}",
        "Documento sintético de prueba para evidenciar el archivo documental de compras.",
        [("Proveedor", f"Proveedor QuetzalMart {i:02d}"), ("Referencia", f"FAC-PROV-DMS-{i:03d}"), ("Estado", "Validada"), ("Total", f"Q {1250 + i * 75:,.2f}"), ("Fecha", "2026-09-28")],
        ["Este archivo corresponde a una factura de proveedor de prueba asociada a una compra confirmada en Odoo.", "Uso: carpeta de facturas de proveedores del módulo Documentos."]
    )

for i in range(1, 6):
    make_pdf(
        OUT / f"contrato_outsourcing_dms_{i:03d}.pdf",
        f"Contrato de outsourcing DMS {i:03d}",
        "Documento sintético de prueba para evidenciar la gestión documental de servicios externos.",
        [("Proveedor", f"Servicios Externos QuetzalMart {i:02d}"), ("Referencia", f"OUT-DMS-{i:03d}"), ("Servicio", "Soporte operativo y logístico"), ("Vigencia", "2026-01-01 a 2026-12-31"), ("Estado", "Vigente")],
        ["El presente documento es una constancia de prueba para el expediente de contratación de servicios externos.", "Uso: carpeta de contratos de outsourcing del módulo Documentos."]
    )

for i in range(1, 6):
    make_pdf(
        OUT / f"contrato_empleado_dms_{i:03d}.pdf",
        f"Contrato de empleado DMS {i:03d}",
        "Documento sintético de prueba para evidenciar la gestión documental de empleados.",
        [("Empleado", f"Empleado de prueba QuetzalMart {i:02d}"), ("Referencia", f"EMP-DMS-{i:03d}"), ("Cargo", "Colaborador operativo"), ("Departamento", "Operaciones"), ("Vigencia", "2026-01-01 a 2026-12-31")],
        ["El presente documento es una constancia de prueba para el expediente laboral del empleado indicado.", "Uso: carpeta de contratos de empleados del módulo Documentos."]
    )

print(f"Created {len(list(OUT.glob('*.pdf')))} PDFs in {OUT}")
