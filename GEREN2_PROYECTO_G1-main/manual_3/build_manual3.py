from __future__ import annotations

import html
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Line, Rect, String


HERE = Path(__file__).resolve().parent
CHARTS = HERE / "graficos"
OUTPUT = HERE / "QuetzalMart · Manual 3 · Inteligencia de negocios con GA4.pdf"
OLD_PDF = OUTPUT

NAVY = colors.HexColor("#11196F")
ORANGE = colors.HexColor("#F14924")
INK = colors.HexColor("#252B36")
MUTED = colors.HexColor("#687181")
PALE = colors.HexColor("#F4F5FA")
PALE_ORANGE = colors.HexColor("#FFF1E9")
GRID = colors.HexColor("#DEE2EB")
GREEN = colors.HexColor("#19866D")
SLATE = colors.HexColor("#778199")

CHANNEL_SESSIONS = [("Email", 15, "15"), ("Direct", 14, "14"), ("Unassigned", 8, "8")]
CHANNEL_REVENUE = [
    ("Email", 274.22, "Q274,22"),
    ("Unassigned", 75.89, "Q75,89"),
    ("Direct", 54.80, "Q54,80"),
]
ECOM_EVENTS = [
    ("view_item", 25, "25 · 7 usuarios"),
    ("add_to_cart", 18, "18 · 5 usuarios"),
    ("begin_checkout", 28, "28 · 5 usuarios"),
    ("purchase", 10, "10 · 4 usuarios"),
]
PRODUCTS = [
    ("Arroz premium 1 kg", 11, "11 unidades · Q149,16"),
    ("Azúcar blanca 1 kg", 3, "3 unidades · Q61,11"),
    ("Frijol negro 1 kg", 1, "1 unidad · Q16,96"),
    ("Atún en agua 140 g", 0, "0 unidades · Q0,00"),
]
CAMPAIGN = [
    ("beneficios_temporada…", 106.42, "Q106,42 · 2 sesiones"),
    ("(not set)", 38.56, "Q38,56 · atribución incompleta"),
]


def fmt_es(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def svg_color(value) -> str:
    if isinstance(value, str):
        if value.startswith("0x"):
            return "#" + value[2:]
        return value
    return "#{:02x}{:02x}{:02x}".format(
        round(value.red * 255),
        round(value.green * 255),
        round(value.blue * 255),
    )


def svg_chart(
    filename: str,
    title: str,
    subtitle: str,
    rows: list[tuple[str, float, str]],
    max_value: float,
    ticks: list[tuple[float, str]],
    footnote: str,
    colors_by_row: list[str] | None = None,
) -> None:
    width, height = 1000, 390
    left, right, top, bottom = 345, 920, 98, 328
    plot_width = right - left
    n = len(rows)
    row_h = (bottom - top) / max(1, n)
    palette = colors_by_row or ["#19866D"] * n
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title id=\"title\">{html.escape(title)}</title>",
        f"<desc id=\"desc\">{html.escape(subtitle + '. ' + footnote)}</desc>",
        "<style>text{font-family:Arial,Helvetica,sans-serif;fill:#252b36}.title{font-size:24px;font-weight:700}.sub{font-size:15px;fill:#687181}.label{font-size:16px}.tick{font-size:13px;fill:#687181}.value{font-size:15px;font-weight:700}.grid{stroke:#dee2eb;stroke-width:1}.axis{stroke:#8991a2;stroke-width:1.2}</style>",
        f'<text class="title" x="30" y="36">{html.escape(title)}</text>',
        f'<text class="sub" x="30" y="62">{html.escape(subtitle)}</text>',
    ]
    for tick, label in ticks:
        x = left + (tick / max_value) * plot_width
        out.append(f'<line class="grid" x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{bottom+1}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{bottom+23}" text-anchor="middle">{html.escape(label)}</text>')
    for i, (label, value, display) in enumerate(rows):
        cy = top + row_h * i + row_h * 0.53
        bar_h = min(26, row_h * 0.56)
        bar_w = max(2, value / max_value * plot_width)
        label_x = left - 15
        out.append(f'<text class="label" x="{label_x}" y="{cy+5:.1f}" text-anchor="end">{html.escape(label)}</text>')
        out.append(f'<rect x="{left}" y="{cy-bar_h/2:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" fill="{svg_color(palette[i])}"/>')
        value_x = min(right - 2, left + bar_w + 10)
        anchor = "end" if value_x >= right - 10 else "start"
        out.append(f'<text class="value" x="{value_x:.1f}" y="{cy+5:.1f}" text-anchor="{anchor}">{html.escape(display)}</text>')
    out.extend([
        f'<line class="axis" x1="{left}" y1="{bottom+1}" x2="{right}" y2="{bottom+1}"/>',
        f'<text class="sub" x="30" y="{height-12}">{html.escape(footnote)}</text>',
        "</svg>",
    ])
    (CHARTS / filename).write_text("\n".join(out), encoding="utf-8")


def build_svgs() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    svg_chart(
        "01_sesiones_por_campana.svg",
        "Sesiones por canal principal de la sesión",
        "GA4 · 4 sept–1 oct 2026 · 37 sesiones",
        CHANNEL_SESSIONS,
        20,
        [(0, "0"), (5, "5"), (10, "10"), (15, "15"), (20, "20")],
        "Las filas concilian con el total de sesiones del informe.",
        [GREEN, NAVY.hexval(), ORANGE.hexval()],
    )
    svg_chart(
        "02_ingresos_por_campana.svg",
        "Ingresos totales por canal principal de la sesión",
        "GA4 · 4 sept–1 oct 2026 · total Q404,91",
        CHANNEL_REVENUE,
        360,
        [(0, "Q0"), (90, "Q90"), (180, "Q180"), (270, "Q270"), (360, "Q360")],
        "La dimensión es grupo de canales; Email no identifica por sí sola una campaña.",
        [GREEN, ORANGE, NAVY.hexval()],
    )
    svg_chart(
        "03_eventos_por_campana.svg",
        "Eventos del recorrido de comercio electrónico",
        "GA4 · 4 sept–1 oct 2026 · eventos y usuarios por evento",
        ECOM_EVENTS,
        40,
        [(0, "0"), (10, "10"), (20, "20"), (30, "30"), (40, "40")],
        "Son cantidades de eventos, no pasos de un embudo secuencial.",
        [NAVY.hexval(), GREEN, ORANGE, "#C2522D"],
    )
    svg_chart(
        "04_productos_mas_vendidos.svg",
        "Artículos comprados por producto",
        "GA4 · 4 sept–1 oct 2026 · unidades compradas e ingresos del artículo",
        PRODUCTS,
        16,
        [(0, "0"), (4, "4"), (8, "8"), (12, "12"), (16, "16")],
        "El importe junto a cada barra es el ingreso del artículo informado por GA4.",
        [GREEN, NAVY.hexval(), ORANGE, SLATE.hexval()],
    )
    svg_chart(
        "05_campana_30sep.svg",
        "Ingresos por campaña de sesión",
        "GA4 · corte independiente del 30 septiembre 2026 · total Q144,98",
        CAMPAIGN,
        180,
        [(0, "Q0"), (45, "Q45"), (90, "Q90"), (135, "Q135"), (180, "Q180")],
        "La tabla diaria suma 26 sesiones por fila frente a 21 en el total del informe.",
        [GREEN, ORANGE],
    )


def chart_drawing(
    title: str,
    subtitle: str,
    rows: list[tuple[str, float, str]],
    max_value: float,
    footnote: str,
    row_colors: list[colors.Color] | None = None,
) -> Drawing:
    width, height = 499, 186
    left, right, top, bottom = 145, 488, 57, 156
    plot_width = right - left
    d = Drawing(width, height)
    d.add(String(0, height - 17, title, fontName="Helvetica-Bold", fontSize=12, fillColor=NAVY))
    d.add(String(0, height - 34, subtitle, fontName="Helvetica", fontSize=7.8, fillColor=MUTED))
    n = len(rows)
    row_h = (bottom - top) / max(1, n)
    palette = row_colors or [GREEN] * n
    for step in range(5):
        x = left + plot_width * step / 4
        d.add(Line(x, top - 2, x, bottom + 2, strokeColor=GRID, strokeWidth=0.6))
    for i, (label, value, display) in enumerate(rows):
        cy = bottom - row_h * i - row_h * 0.52
        d.add(String(0, cy - 3, label[:24], fontName="Helvetica", fontSize=7.8, fillColor=INK))
        bar_w = max(1.5, plot_width * value / max_value)
        d.add(Rect(left, cy - 5.8, bar_w, 11.6, rx=3, ry=3, fillColor=palette[i], strokeColor=None))
        tx = min(right - 2, left + bar_w + 5)
        d.add(String(tx, cy - 3, display, fontName="Helvetica-Bold", fontSize=7.4, fillColor=INK))
    d.add(Line(left, top - 3, right, top - 3, strokeColor=SLATE, strokeWidth=0.6))
    d.add(String(0, 8, footnote[:110], fontName="Helvetica", fontSize=7.1, fillColor=MUTED))
    return d


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("QMTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8),
        "deck": ParagraphStyle("QMDeck", parent=base["Normal"], fontName="Helvetica", fontSize=11, leading=15, textColor=MUTED, spaceAfter=12),
        "h1": ParagraphStyle("QMH1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceBefore=4, spaceAfter=9, keepWithNext=True),
        "h2": ParagraphStyle("QMH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=ORANGE, spaceBefore=8, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("QMBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.1, leading=13, textColor=INK, spaceAfter=6),
        "small": ParagraphStyle("QMSmall", parent=base["BodyText"], fontName="Helvetica", fontSize=7.6, leading=10, textColor=MUTED, spaceAfter=4),
        "cell": ParagraphStyle("QMCell", parent=base["BodyText"], fontName="Helvetica", fontSize=7.5, leading=9.3, textColor=INK),
        "cellbold": ParagraphStyle("QMCellBold", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.3, textColor=INK),
        "cellhead": ParagraphStyle("QMCellHead", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.3, textColor=colors.white),
        "callout": ParagraphStyle("QMCallout", parent=base["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=NAVY),
        "kpi": ParagraphStyle("QMKPI", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=NAVY, alignment=TA_CENTER),
        "kpismall": ParagraphStyle("QMKPISmall", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=MUTED, alignment=TA_CENTER),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def make_table(rows: list[list[str]], widths: list[float], st, header=True):
    data = []
    for r_i, row in enumerate(rows):
        style = st["cellhead"] if header and r_i == 0 else st["cell"]
        data.append([Paragraph(str(value), style) for value in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ])
    else:
        commands.append(("BACKGROUND", (0, 0), (-1, -1), PALE))
    t.setStyle(TableStyle(commands))
    return t


def kpi_table(st):
    labels = [
        ("Sesiones", "37"),
        ("Eventos", "482"),
        ("Ingresos GA4", "Q404,91"),
        ("Compradores", "4 / 7"),
        ("Artículos", "15"),
    ]
    cells = []
    for label, value in labels:
        cells.append([
            Paragraph(f"<font color='#687181'>{label}</font>", st["kpismall"]),
            Spacer(1, 2),
            Paragraph(f"<font color='#11196F'>{value}</font>", st["kpi"]),
        ])
    t = Table([cells], colWidths=[99.5] * 5, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def page_frame(c: canvas.Canvas, doc) -> None:
    c.saveState()
    w, h = A4
    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.circle(24, h - 25, 7, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.circle(24, h - 25, 3.2, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.3)
    c.drawString(38, h - 27, "QUETZALMART  /  INTELIGENCIA DE NEGOCIOS")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawRightString(w - 48, h - 27, "GA4 · CORTE 2 OCT 2026")
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.6)
    c.line(48, h - 39, w - 48, h - 39)
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.65)
    c.line(48, 35, w - 48, 35)
    c.setFont("Helvetica", 7)
    c.setFillColor(MUTED)
    c.drawString(48, 23, "GERENCIALES 2 · PROYECTO 2026")
    c.drawRightString(w - 48, 23, f"PÁGINA {doc.page + 1}")
    c.restoreState()


def draw_cover_overlay(path: Path) -> Path:
    overlay = path
    c = canvas.Canvas(str(overlay), pagesize=A4)
    c.setFillColor(colors.white)
    c.rect(63, 15, 260, 15, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica", 6.3)
    c.drawString(66, 20, "Versión 1.1 · Actualizado 2 de octubre de 2026 · Página 1")
    c.save()
    return overlay


def build_content(path: Path) -> None:
    st = styles()
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=57,
        bottomMargin=48,
        title="QuetzalMart · Manual 3 · Inteligencia de negocios con GA4",
        author="QuetzalMart · GERENCIALES 2",
        subject="Lectura de negocio con indicadores y gráficos de Google Analytics 4",
    )
    frame = Frame(48, 48, A4[0] - 96, A4[1] - 105, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="branded", frames=[frame], onPage=page_frame)])
    story = []
    story += [
        p("Manual 3", st["h2"]),
        p("Inteligencia de negocios con GA4", st["title"]),
        p("Indicadores del comercio electrónico, adquisición, artículos y exploraciones de QuetzalMart.", st["deck"]),
        p("<b>Resumen ejecutivo</b>", st["h2"]),
        p("En los últimos 28 días disponibles (4 sept–1 oct 2026), la propiedad presenta 37 sesiones, 482 eventos y Q404,91 de ingresos totales. El evento purchase registra 10 eventos y 4 usuarios. El informe por artículo suma Q227,23; la diferencia frente a ingresos totales se marca para revisión, no se oculta ni se trata como conciliada.", st["body"]),
        kpi_table(st),
        Spacer(1, 9),
        p("<b>Cómo leer el corte.</b> Los indicadores generales abarcan 4 sept–1 oct. Las exploraciones están en 27 sept–2 oct. El análisis UTM de beneficios_temporada_2026 corresponde a un solo día, 30 sept. Son ventanas distintas y se presentan por separado.", st["callout"]),
        p("Indicadores clave", st["h2"]),
        make_table([
            ["Métrica", "Resultado", "Definición / cautela"],
            ["Sesiones con interacción", "17 (45,95 %)", "Tasa de interacción mostrada por GA4."],
            ["Eventos clave", "10; tasa por sesión 18,92 %", "Incluye todos los eventos marcados como clave, no solo purchase."],
            ["Compradores activos", "4 de 7 (57,14 %)", "Cálculo propio por usuario: usuarios con purchase ÷ usuarios activos."],
        ], [125, 132, 242], st),
        PageBreak(),
        p("01  /  Adquisición", st["h1"]),
        p("El informe Adquisición de tráfico usa la dimensión Grupo de canales principal de la sesión. Las filas visibles concilian con 37 sesiones y Q404,91.", st["body"]),
        chart_drawing("Sesiones por canal principal de sesión", "Últimos 28 días disponibles · total 37 sesiones", CHANNEL_SESSIONS, 20, "Las filas suman el total del informe.", [GREEN, NAVY, ORANGE]),
        Spacer(1, 8),
        chart_drawing("Ingresos totales por canal", "Misma propiedad y mismo periodo · total Q404,91", CHANNEL_REVENUE, 360, "Email es grupo de canal, no nombre de campaña.", [GREEN, ORANGE, NAVY]),
        Spacer(1, 8),
        make_table([
            ["Canal", "Sesiones", "Interacción", "Eventos", "Eventos clave", "Tasa clave/sesión", "Ingresos"],
            ["Email", "15", "6 (40 %)", "210", "5", "26,67 %", "Q274,22"],
            ["Direct", "14", "10 (71,43 %)", "194", "4", "14,29 %", "Q54,80"],
            ["Unassigned", "8", "1 (12,5 %)", "78", "1", "12,50 %", "Q75,89"],
            ["Total", "37", "17 (45,95 %)", "482", "10", "18,92 %", "Q404,91"],
        ], [58, 55, 78, 48, 70, 95, 95], st),
        Spacer(1, 6),
        p("Email representa Q274,22 (67,72 %) de los ingresos de la tabla. La tasa de evento clave reúne eventos clave de cualquier nombre; no se debe llamar tasa de compra.", st["small"]),
        PageBreak(),
        p("02  /  Comercio electrónico", st["h1"]),
        p("El informe Eventos registra los cuatro eventos solicitados. Sus cantidades son eventos, no usuarios únicos ni una secuencia de embudo.", st["body"]),
        chart_drawing("Volumen observado de eventos", "Eventos y usuarios por evento · 4 sept–1 oct", ECOM_EVENTS, 40, "Los conteos pueden repetirse por persona; no equivalen a pasos completados.", [NAVY, GREEN, ORANGE, colors.HexColor("#C2522D")]),
        Spacer(1, 10),
        make_table([
            ["Evento", "Eventos", "Usuarios"],
            ["view_item", "25", "7"],
            ["add_to_cart", "18", "5"],
            ["begin_checkout", "28", "5"],
            ["purchase", "10", "4"],
        ], [220, 120, 120], st),
        Spacer(1, 10),
        p("Conversión a nivel de usuario", st["h2"]),
        p("<b>4 usuarios con purchase ÷ 7 usuarios activos = 57,14 %.</b> Es una proporción calculada desde usuarios del informe de eventos; no es la tasa por sesión de GA4. El 18,92 % del informe de adquisición corresponde a todos los eventos clave configurados.", st["body"]),
        p("Las cantidades de begin_checkout pueden superar las de add_to_cart porque una misma persona puede activar repetidamente un evento. Para evaluar abandono se requiere que la exploración de embudo muestre usuarios en cada paso.", st["callout"]),
        PageBreak(),
        p("03  /  Productos", st["h1"]),
        p("El informe Compras en comercio electrónico ofrece el ranking real de artículos comprados y sus ingresos durante el periodo principal.", st["body"]),
        chart_drawing("Artículos comprados por producto", "Unidades compradas; etiqueta adicional muestra ingresos por artículo", PRODUCTS, 16, "Arroz premium lidera en unidades e ingresos del artículo.", [GREEN, NAVY, ORANGE, SLATE]),
        Spacer(1, 10),
        make_table([
            ["Producto", "Vistos", "Al carrito", "Comprados", "Ingresos del artículo"],
            ["Arroz premium 1 kg", "22", "16", "11", "Q149,16"],
            ["Azúcar blanca 1 kg", "2", "2", "3", "Q61,11"],
            ["Frijol negro 1 kg", "0", "0", "1", "Q16,96"],
            ["Atún en agua 140 g", "1", "0", "0", "Q0,00"],
            ["Total", "25", "18", "15", "Q227,23"],
        ], [160, 50, 60, 70, 159], st),
        Spacer(1, 12),
        p("<b>Alerta de conciliación:</b> GA4 muestra Q404,91 como ingresos totales y Q227,23 como ingresos por artículo para el mismo periodo. No se suman ni se presentan como cifras equivalentes; revisar los parámetros de compra y la composición de estas métricas antes de sacar conclusiones contables.", st["callout"]),
        PageBreak(),
        p("04  /  Campaña identificada", st["h1"]),
        p("Este corte es exclusivamente del 30 de septiembre de 2026 y se mantiene separado de los últimos 28 días.", st["body"]),
        chart_drawing("Ingresos del corte por campaña", "30 septiembre 2026 · total de ingresos Q144,98", CAMPAIGN, 180, "Las filas de sesión no concilian con el total del informe.", [GREEN, ORANGE]),
        Spacer(1, 10),
        make_table([
            ["Campaña", "Sesiones visibles", "Eventos clave", "Ingresos"],
            ["beneficios_temporada_2026", "2", "1", "Q106,42"],
            ["(not set)", "12", "1", "Q38,56"],
            ["Total del informe", "21", "2", "Q144,98"],
        ], [220, 95, 85, 100], st),
        Spacer(1, 12),
        p("La campaña identificada aparece asociada con Q106,42. La tabla vista solo indica “Eventos clave” y no muestra ahí el nombre del evento; no afirmar que ese evento fue purchase hasta abrir el desglose por nombre.", st["body"]),
        p("<b>Advertencia visible de GA4:</b> las filas mostradas suman 26 sesiones, frente a 21 del total; además, hay una alerta de atribución para (not set). Por eso, el informe diario demuestra la existencia de una campaña identificada, pero no sirve para afirmar que el reparto de sesiones esté conciliado.", st["callout"]),
        PageBreak(),
        p("05  /  Segmentos y exploraciones", st["h1"]),
        p("La primera exploración guardada sí contiene una comparación de segmentos para 27 sept–2 oct 2026.", st["body"]),
        make_table([
            ["Segmento de usuarios", "Usuarios activos"],
            ["Usuarios con visualizacion de producto", "7"],
            ["Usuarios con carrito", "5"],
            ["Usuarios compradores", "4"],
        ], [325, 174], st),
        Spacer(1, 8),
        p("Cinco segmentos de eventos", st["h2"]),
        make_table([
            ["Segmento guardado", "Evento que delimita"],
            ["Evento view_item", "view_item"],
            ["Evento add_to_cart", "add_to_cart"],
            ["Evento begin_checkout", "begin_checkout"],
            ["Evento purchase", "purchase"],
            ["Evento session_start", "session_start"],
        ], [250, 249], st),
        Spacer(1, 8),
        p("Audiencias configuradas", st["h2"]),
        make_table([
            ["Audiencia", "Tipo / propósito"],
            ["GA4 sugerida - Vistas de producto", "Sugerida · interés en productos"],
            ["GA4 sugerida - Checkout sin compra", "Sugerida · seguimiento de checkout"],
            ["GA4 personalizada - Visitantes sin compra", "Personalizada · visitantes sin purchase"],
        ], [270, 229], st),
        Spacer(1, 6),
        p("La comparación 7 / 5 / 4 es población de segmentos y no se debe sumar como usuarios únicos. Las audiencias son elementos distintos de los segmentos y se muestran por separado en GA4.", st["small"]),
        PageBreak(),
        p("06  /  Abandono y presentación", st["h1"]),
        p("La segunda exploración guardada, Exploración 2 - Eventos y abandono de carrito, tiene configurado el embudo estándar Agrega producto al carrito → Compra completada para 27 sept–2 oct 2026. La tabla ya muestra <b>5 usuarios</b> que agregaron al carrito y <b>4 compradores (80 %)</b>.", st["body"]),
        p("El embudo registra <b>1 abandono (20 %)</b> en ese periodo. Esta es una medición secuencial; los totales generales de eventos add_to_cart y purchase no sustituyen esta exploración.", st["callout"]),
        p("Ruta recomendada para mostrar el análisis", st["h2"]),
        make_table([
            ["Paso", "Qué abrir y explicar"],
            ["1", "Seleccionar la propiedad QuetzalMart Web 2026."],
            ["2", "Adquisición de tráfico · últimos 28 días · sesiones, canales e ingresos."],
            ["3", "Eventos · view_item, add_to_cart, begin_checkout y purchase."],
            ["4", "Compras en comercio electrónico · productos, unidades e ingresos por artículo."],
            ["5", "Exploración 1 · comparación 7 / 5 / 4 usuarios."],
            ["6", "Exploración 2 · mostrar 5 carritos, 4 compras y 1 abandono (20 %)."],
            ["7", "Corte 30 sept · campaña beneficios_temporada_2026, Q106,42, con advertencias."],
            ["8", "Comparar pedidos e invoices con Odoo; GA4 mide comportamiento web, Odoo conserva el registro comercial."],
        ], [58, 441], st),
        Spacer(1, 8),
        p("<b>Acciones de mejora:</b> revisar la diferencia entre ingresos totales y por artículo; comprobar el desglose del evento clave de campaña; y verificar el periodo de la exploración cuando se presenten nuevos datos. No presentar como verificado ningún resultado que no aparezca en pantalla.", st["body"]),
    ]
    doc.build(story)


def main() -> None:
    build_svgs()
    with tempfile.TemporaryDirectory(prefix="qm_m3_") as temp:
        temp_path = Path(temp)
        content_pdf = temp_path / "content.pdf"
        overlay_pdf = temp_path / "cover-overlay.pdf"
        final_pdf = temp_path / "final.pdf"
        build_content(content_pdf)
        draw_cover_overlay(overlay_pdf)
        old_reader = PdfReader(str(OLD_PDF))
        content_reader = PdfReader(str(content_pdf))
        overlay_reader = PdfReader(str(overlay_pdf))
        writer = PdfWriter()
        cover = old_reader.pages[0]
        cover.merge_page(overlay_reader.pages[0])
        writer.add_page(cover)
        for page in content_reader.pages:
            writer.add_page(page)
        writer.add_metadata({
            "/Title": "QuetzalMart · Manual 3 · Inteligencia de negocios con GA4",
            "/Author": "QuetzalMart · GERENCIALES 2",
            "/Subject": "Indicadores, artículos, adquisición y exploraciones de Google Analytics 4",
        })
        with final_pdf.open("wb") as stream:
            writer.write(stream)
        final_pdf.replace(OUTPUT)
    print(f"PDF actualizado: {OUTPUT}")
    print(f"Páginas totales: {len(PdfReader(str(OUTPUT)).pages)}")


if __name__ == "__main__":
    main()
