"""Create a revised Manual 3 without changing the historical source PDF."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "QuetzalMart · Manual 3 · Inteligencia de negocios con GA4.pdf"
OUTPUT = HERE / "QuetzalMart · Manual 3 · Inteligencia de negocios con GA4.pdf"

NAVY = colors.HexColor("#11196F")
ORANGE = colors.HexColor("#F14924")
INK = colors.HexColor("#252B36")
MUTED = colors.HexColor("#687181")
PALE = colors.HexColor("#F4F5FA")
GRID = colors.HexColor("#DEE2EB")
PAGE_W, PAGE_H = A4
LEFT = 48
WIDTH = PAGE_W - 96

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.1, leading=13, textColor=INK)
SMALL = ParagraphStyle("small", fontName="Helvetica", fontSize=7.8, leading=10.8, textColor=MUTED)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5, leading=10, textColor=INK)
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=colors.white)


def paragraph(c, text, y, style=BODY, gap=8):
    item = Paragraph(text, style)
    _, height = item.wrap(WIDTH, PAGE_H)
    item.drawOn(c, LEFT, y - height)
    return y - height - gap


def heading(c, text, y, level=1):
    c.setFillColor(NAVY if level == 1 else ORANGE)
    c.setFont("Helvetica-Bold", 17 if level == 1 else 11)
    c.drawString(LEFT, y, text)
    return y - (25 if level == 1 else 18)


def table(c, rows, widths, y, gap=10):
    data = [[Paragraph(str(v), HEAD if i == 0 else CELL) for v in row] for i, row in enumerate(rows)]
    item = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    item.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    _, height = item.wrap(WIDTH, PAGE_H)
    item.drawOn(c, LEFT, y - height)
    return y - height - gap


def frame(c, page):
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.circle(24, PAGE_H - 25, 7, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.circle(24, PAGE_H - 25, 3.2, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.3)
    c.drawString(38, PAGE_H - 27, "QUETZALMART  /  INTELIGENCIA DE NEGOCIOS")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawRightString(PAGE_W - LEFT, PAGE_H - 27, "GA4 · REVISIÓN 7 OCT 2026")
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.6)
    c.line(LEFT, PAGE_H - 39, PAGE_W - LEFT, PAGE_H - 39)
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.65)
    c.line(LEFT, 35, PAGE_W - LEFT, 35)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawString(LEFT, 23, "GERENCIALES 2 · PROYECTO 2026")
    c.drawRightString(PAGE_W - LEFT, 23, f"PÁGINA {page}")


def replacement_pages():
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=A4)

    frame(c, 2)
    y = PAGE_H - 66
    y = heading(c, "Manual 3", y, 2)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(LEFT, y - 11, "Inteligencia de negocios con GA4")
    y -= 47
    y = paragraph(c, "Indicadores del comercio electrónico, adquisición, artículos y exploraciones de QuetzalMart.", y, SMALL, 18)
    y = heading(c, "Resumen ejecutivo", y, 2)
    y = paragraph(c, "En el corte histórico de 4 sept-1 oct 2026, la propiedad presenta 37 sesiones, 482 eventos y Q404,91 de ingresos totales. El evento purchase registra 10 eventos y 4 usuarios. El informe por artículo suma Q227,23; la diferencia frente a ingresos totales se marca para revisión, no se presenta como conciliada.", y)
    y = table(c, [
        ["Sesiones", "Eventos", "Ingresos GA4", "Compradores", "Artículos"],
        ["37", "482", "Q404,91", "4 / 7", "15"],
    ], [100, 100, 100, 100, 99], y, gap=14)
    y = paragraph(c, "<b>Cómo leer los cortes.</b> Los indicadores generales abarcan 4 sept-1 oct; la comparación histórica de usuarios, 27 sept-2 oct; la Exploración 2 actual, 28 sept-6 oct; y la campaña beneficios_temporada_2026, solo el 30 sept. Son ventanas distintas y se presentan por separado.", y)
    y = heading(c, "Indicadores clave", y - 13, 2)
    y = table(c, [
        ["Métrica", "Resultado", "Definición / cautela"],
        ["Sesiones con interacción", "17 (45,95 %)", "Tasa de interacción mostrada por GA4."],
        ["Eventos clave", "10; tasa por sesión 18,92 %", "Incluye todos los eventos marcados como clave, no solo purchase."],
        ["Compradores activos", "4 de 7 (57,14 %)", "Cálculo histórico: usuarios con purchase entre usuarios activos."],
    ], [125, 132, 242], y)
    y = paragraph(c, "Este resumen mantiene el corte original. Las páginas 7-9 se revisaron el 7 oct 2026 para documentar la configuración actual de las dos exploraciones.", y, SMALL)
    if y < 47:
        raise ValueError(f"Page 2 overflow: y={y}")
    c.showPage()

    frame(c, 7)
    y = heading(c, "05  /  Segmentos y exploraciones", PAGE_H - 66)
    y = paragraph(c, "La rúbrica solicita <b>tres segmentos de usuarios</b>, <b>cinco segmentos de eventos</b> y <b>dos informes de exploración</b> creados con ellos. Las dos exploraciones guardadas tienen funciones diferentes.", y)
    y = heading(c, "Exploración 1 - segmentos de usuarios", y - 9, 2)
    y = table(c, [
        ["Segmento de usuarios", "Condición", "Qué compara"],
        ["Usuarios con visualización de producto", "view_item", "Personas que vieron un producto"],
        ["Usuarios con carrito", "add_to_cart", "Personas que añadieron al carrito"],
        ["Usuarios compradores", "purchase", "Personas que compraron"],
    ], [210, 88, 201], y)
    y = paragraph(c, "En la consulta histórica del <b>27 sept-2 oct 2026</b> se observaron 7 / 5 / 4 usuarios activos, respectivamente (anexo A11-A12). Antes de presentar, comprobar el periodo elegido en pantalla; una fecha distinta puede cambiar estos valores. Los segmentos se superponen y no deben sumarse.", y, SMALL)
    y = heading(c, "Exploración 2 - segmentos de eventos", y - 10, 2)
    y = paragraph(c, "La exploración guardada <b>Exploración 2 - Segmentos de eventos</b> contiene los cinco segmentos siguientes. En la consulta del <b>28 sept-6 oct 2026</b>, la métrica visible fue <b>Número de eventos</b>:", y)
    y = table(c, [
        ["Segmento de eventos", "Condición", "Eventos observados", "Dónde se muestra"],
        ["Evento view_item", "view_item", "34", "Pestaña: Comparación de 4 eventos"],
        ["Evento add_to_cart", "add_to_cart", "27", "Pestaña: Comparación de 4 eventos"],
        ["Evento begin_checkout", "begin_checkout", "49", "Pestaña: Comparación de 4 eventos"],
        ["Evento purchase", "purchase", "19", "Pestaña: Comparación de 4 eventos"],
        ["Evento session_start", "session_start", "47", "Pestaña: Evento session_start - sesiones"],
    ], [136, 100, 92, 171], y)
    y = paragraph(c, "<b>Diferencia de alcance:</b> un segmento de usuarios reúne a las personas que cumplieron una condición; un segmento de eventos selecciona las ocurrencias del evento que cumplen la condición. Es válido que ambos usen, por ejemplo, <i>add_to_cart</i>, pero no miden lo mismo. Estos cinco totales no forman un embudo secuencial ni una tasa de abandono.", y, SMALL)
    y = paragraph(c, "Fuente de la revisión: propiedad QuetzalMart Web 2026, Exploraciones guardadas 1 y 2, consultadas el 7 oct 2026. Los conteos cambian al modificar el intervalo o al llegar nuevos datos.", y, SMALL)
    if y < 47:
        raise ValueError(f"Page 7 overflow: y={y}")
    c.showPage()

    frame(c, 8)
    y = heading(c, "06  /  Exploración 2 y presentación", PAGE_H - 66)
    y = paragraph(c, "Para el inciso <b>1.25 - Exploraciones</b>, abrir las dos exploraciones guardadas. La primera compara tres segmentos de usuarios; la segunda presenta cinco segmentos de eventos en <b>dos pestañas</b>. En la primera se comparan view_item, add_to_cart, begin_checkout y purchase. En la segunda se muestra session_start. Señalar los nombres en COMPARACIONES DE SEGMENTOS y la métrica Número de eventos.", y)
    y = paragraph(c, "<b>No confundir con el inciso 1.23:</b> el informe Recorrido de compra demuestra el abandono del carrito. El antiguo embudo de la Exploración 2, conservado en las figuras A17-A18, es una <b>captura histórica</b> del 27 sept-2 oct 2026: 5 usuarios añadieron al carrito, 4 compraron y 1 abandonó (20 %). Ya no describe la configuración actual de la Exploración 2.", y)
    y = heading(c, "Ruta recomendada para la exposición", y - 3, 2)
    y = table(c, [
        ["Paso", "Qué abrir y explicar"],
        ["1", "Seleccionar la propiedad QuetzalMart Web 2026 y fijar el periodo a demostrar."],
        ["2", "Informes > Adquisición de tráfico: sesiones, canales e ingresos."],
        ["3", "Informes > Eventos: view_item, add_to_cart, begin_checkout y purchase."],
        ["4", "Compras en comercio electrónico: productos, unidades e ingresos por artículo."],
        ["5", "Recorrido de compra: mostrar el abandono del carrito para el inciso 1.23."],
        ["6", "Exploración 1: tres segmentos de usuarios y su comparación."],
        ["7", "Exploración 2: abrir ambas pestañas y mostrar los cinco segmentos de eventos (4 + 1)."],
        ["8", "Indicar el periodo de cada vista. Comparar los pedidos con Odoo por separado."],
    ], [58, 441], y)
    y = heading(c, "Cómo explicar las cifras", y - 3, 2)
    y = paragraph(c, "Las cifras <b>34, 27, 49, 19 y 47</b> corresponden a eventos observados en la revisión del 28 sept-6 oct 2026, no a usuarios únicos ni a etapas consecutivas. Por eso begin_checkout puede superar add_to_cart. Al presentar, leer las cifras actuales en GA4; no repetir automáticamente los valores históricos de este manual.", y)
    y = paragraph(c, "Fuente en vivo: Exploración 2 - Segmentos de eventos, propiedad QuetzalMart Web 2026. Las figuras A17-A18 del anexo solo respaldan el estado anterior del embudo, no la configuración revisada.", y, SMALL)
    if y < 47:
        raise ValueError(f"Page 8 overflow: y={y}")
    c.showPage()

    frame(c, 9)
    y = heading(c, "Anexo A  /  Capturas de GA4", PAGE_H - 66)
    y = paragraph(c, "Propiedad QuetzalMart Web 2026. Las capturas A01-A18 se tomaron el <b>6 de octubre de 2026</b> y documentan consultas históricas. Las páginas 7 y 8 de esta versión fueron revisadas el 7 de octubre para reflejar la configuración actual de las exploraciones; las demás páginas conservan sus cortes originales.", y)
    y = paragraph(c, "<b>Periodos distintos:</b> informes principales, 4 sept-1 oct; campaña, 30 sept; exploraciones históricas, 27 sept-2 oct. La exploración de cinco segmentos de eventos revisada usa 28 sept-6 oct. Nunca comparar sus totales sin igualar primero las fechas.", y, SMALL)
    y = paragraph(c, "<b>Nota de consulta:</b> la campaña del 30 de septiembre mostró posteriormente 27 sesiones y Q350,11 (Q222,10 para beneficios_temporada_2026), mientras el cuerpo original transcribe 21 sesiones, Q144,98 y Q106,42. Se conserva esa diferencia sin atribuirle una causa no comprobada.", y, SMALL)
    y = paragraph(c, "<b>Exploraciones:</b> A11-A12 documentan la comparación histórica de usuarios; A13 documenta los cinco segmentos guardados. A17-A18 registran el embudo anterior de Exploración 2 y se conservan únicamente como evidencia histórica, no como captura de la vista actual.", y, SMALL)
    y = heading(c, "Índice de figuras", y - 12, 2)
    figure_rows = [
        ("A01", "Adquisición: sesiones por canal", "10"),
        ("A02", "Adquisición: desglose de sesiones", "11"),
        ("A03", "Adquisición: eventos e ingresos por canal", "12"),
        ("A04", "Eventos: series del comercio electrónico", "13"),
        ("A05", "Eventos: cantidades y usuarios", "14"),
        ("A06", "Productos: actividad por artículo", "15"),
        ("A07", "Productos: unidades e ingresos", "16"),
        ("A08", "Campaña: corte diario original", "17"),
        ("A09", "Campaña: ingresos y eventos clave", "18"),
        ("A10", "Campaña: sesiones y advertencia", "19"),
        ("A11", "Segmentos: periodo y configuración", "20"),
        ("A12", "Segmentos: usuarios activos", "21"),
        ("A13", "Segmentos: cinco eventos guardados", "22"),
        ("A14", "Audiencias: evolución de usuarios", "23"),
        ("A15", "Audiencias: usuarios y sesiones", "24"),
        ("A16", "Audiencias: sugeridas y personalizada", "25"),
        ("A17", "Embudo anterior: contexto histórico", "26"),
        ("A18", "Embudo anterior: resultado histórico", "27"),
    ]
    y = table(c, [["Figura", "Descripción", "Página"], *figure_rows], [58, 383, 58], y, gap=0)
    if y < 47:
        raise ValueError(f"Page 9 overflow: y={y}")
    c.showPage()
    c.save()
    stream.seek(0)
    return PdfReader(stream)


def cover_revision():
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=A4)
    c.setFillColor(colors.white)
    c.rect(57, 12, 410, 30, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica", 6.5)
    c.drawString(66, 20, "Versión 1.2 · Exploraciones actualizadas 7 de octubre de 2026 · Página 1")
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def main():
    original = PdfReader(str(SOURCE))
    if len(original.pages) != 27:
        raise ValueError(f"Expected 27 source pages, got {len(original.pages)}")
    revised = replacement_pages()
    writer = PdfWriter()
    overlay = cover_revision()
    for index, page in enumerate(original.pages):
        if index == 0:
            page.merge_page(overlay)
            writer.add_page(page)
        elif index in (1, 6, 7, 8):
            writer.add_page(revised.pages[(0 if index == 1 else index - 5)])
        else:
            writer.add_page(page)
    writer.add_metadata({
        "/Title": "QuetzalMart · Manual 3 · Inteligencia de negocios con GA4",
        "/Author": "QuetzalMart · GERENCIALES 2",
        "/Subject": "Manual con exploraciones de segmentos de usuarios y eventos actualizadas al 7 oct 2026",
    })
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    print(f"Created: {OUTPUT}")
    print(f"Pages: {len(PdfReader(str(OUTPUT)).pages)}")


if __name__ == "__main__":
    main()
