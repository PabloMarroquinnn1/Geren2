"""Documentos PDF del gestor documental de QuetzalMart.

* Facturas de proveedor (formato FEL) a partir de las facturas registradas en Odoo.
* Contratos de outsourcing con los proveedores de servicios tercerizados.
* Contratos individuales de trabajo con los datos de Empleados/Contratos.

Las funciones reciben los datos leídos de Odoo (las usa carga_masiva/cargar_quetzalmart.py,
paso "documentos"). Todos los datos son ficticios y para uso académico.
"""
import hashlib
import uuid
from datetime import date, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

RAIZ = Path(__file__).resolve().parents[1]
LOGO = RAIZ / "odoo_addons" / "qm_implementacion" / "static" / "img" / "logo_quetzalmart.png"
VERDE = colors.HexColor("#0B6E4F")
VERDE_OSCURO = colors.HexColor("#064635")
ROJO = colors.HexColor("#C8102E")
CREMA = colors.HexColor("#FFF8E7")
GRIS = colors.HexColor("#5B6B62")

QUETZALMART = {
    "nombre": "QuetzalMart, Sociedad Anónima",
    "nit": "9845123-6",
    "direccion": "Avenida Bolívar 32-17, Zona 4, Ciudad de Guatemala",
    "representante": "Mariana Lucía Ajú Cotí",
    "cargo": "Directora General y Representante Legal",
}

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

estilos = getSampleStyleSheet()
TEXTO = ParagraphStyle("texto", parent=estilos["Normal"], fontName="Helvetica", fontSize=9.5,
                       leading=13.5, alignment=TA_JUSTIFY, spaceAfter=5)
PEQUENO = ParagraphStyle("pequeno", parent=TEXTO, fontSize=7.5, leading=10, textColor=GRIS)
TITULO = ParagraphStyle("titulo", parent=TEXTO, fontName="Helvetica-Bold", fontSize=14, leading=18,
                        alignment=TA_CENTER, textColor=VERDE_OSCURO, spaceAfter=4)
SUBTITULO = ParagraphStyle("subtitulo", parent=TEXTO, fontName="Helvetica-Bold", fontSize=10.5,
                           textColor=VERDE, spaceBefore=6, spaceAfter=3)
DERECHA = ParagraphStyle("derecha", parent=TEXTO, alignment=TA_RIGHT)
CELDA = ParagraphStyle("celda", parent=TEXTO, fontSize=8.5, leading=11, alignment=0, spaceAfter=0)


def quetzales(monto):
    return "Q {:,.2f}".format(monto or 0)


def fecha_larga(valor):
    if isinstance(valor, str):
        valor = datetime.strptime(valor[:10], "%Y-%m-%d").date()
    return f"{valor.day} de {MESES[valor.month - 1]} de {valor.year}"


def numero_a_letras(monto):
    unidades = ["", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
                "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho",
                "diecinueve", "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro",
                "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"]
    decenas = ["", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
    centenas = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos",
                "setecientos", "ochocientos", "novecientos"]

    def menor_mil(n):
        if n == 100:
            return "cien"
        texto = centenas[n // 100]
        resto = n % 100
        if resto < 30:
            parte = unidades[resto]
        else:
            parte = decenas[resto // 10] + (" y " + unidades[resto % 10] if resto % 10 else "")
        return (texto + " " + parte).strip()

    entero = int(monto)
    centavos = int(round((monto - entero) * 100))
    miles, resto = divmod(entero, 1000)
    partes = []
    if miles:
        partes.append("mil" if miles == 1 else menor_mil(miles) + " mil")
    if resto or not partes:
        partes.append(menor_mil(resto) or "cero")
    return f"{' '.join(partes)} quetzales con {centavos:02d}/100".capitalize()


def encabezado_quetzalmart(historia, titulo, subtitulo):
    logo = Image(str(LOGO), width=62 * mm, height=15.5 * mm)
    datos = Paragraph(f"<b>{QUETZALMART['nombre']}</b><br/>NIT {QUETZALMART['nit']}<br/>"
                      f"{QUETZALMART['direccion']}", PEQUENO)
    tabla = Table([[logo, datos]], colWidths=[70 * mm, 110 * mm])
    tabla.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LINEBELOW", (0, 0), (-1, 0), 1.2, VERDE)]))
    historia += [tabla, Spacer(1, 8), Paragraph(titulo, TITULO), Paragraph(subtitulo, ParagraphStyle(
        "s", parent=TEXTO, alignment=TA_CENTER, textColor=GRIS)), Spacer(1, 6)]


def firmas(historia, izquierda, derecha):
    tabla = Table([
        ["", ""],
        ["_" * 38, "_" * 38],
        [Paragraph(izquierda, ParagraphStyle("f", parent=CELDA, alignment=TA_CENTER)),
         Paragraph(derecha, ParagraphStyle("f", parent=CELDA, alignment=TA_CENTER))],
    ], colWidths=[90 * mm, 90 * mm], rowHeights=[24 * mm, None, None])
    tabla.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    historia.append(KeepTogether([Spacer(1, 6), tabla]))


def pie(canvas, documento):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRIS)
    canvas.drawString(18 * mm, 10 * mm, "Documento generado para el proyecto académico SOG2 (QuetzalMart). "
                                        "Datos ficticios.")
    canvas.drawRightString(198 * mm, 10 * mm, f"Página {documento.page}")
    canvas.restoreState()


def construir(ruta, historia):
    documento = SimpleDocTemplate(str(ruta), pagesize=LETTER, leftMargin=18 * mm, rightMargin=18 * mm,
                                  topMargin=14 * mm, bottomMargin=18 * mm, title=ruta.stem,
                                  author="QuetzalMart")
    documento.build(historia, onFirstPage=pie, onLaterPages=pie)
    return ruta


def clausulas(historia, lista):
    for numero, (titulo, texto) in enumerate(lista, 1):
        ordinal = ["PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA", "SEXTA", "SÉPTIMA", "OCTAVA",
                   "NOVENA", "DÉCIMA", "DÉCIMA PRIMERA", "DÉCIMA SEGUNDA", "DÉCIMA TERCERA"][numero - 1]
        historia.append(Paragraph(f"<b>{ordinal}. {titulo}.</b> {texto}", TEXTO))


# ---------------------------------------------------------------------------
def factura_proveedor(carpeta, factura, proveedor, lineas):
    """Factura electrónica (FEL) emitida por el proveedor a QuetzalMart."""
    serie, numero = factura["ref"].split("-")[-2], factura["ref"].split("-")[-1]
    autorizacion = str(uuid.UUID(hashlib.md5(factura["ref"].encode()).hexdigest())).upper()
    ruta = Path(carpeta) / f"Factura proveedor {factura['ref']}.pdf"
    historia = []
    emisor = Table([[
        Paragraph(f"<font size=13 color='#064635'><b>{proveedor['name']}</b></font><br/>"
                  f"NIT {proveedor.get('vat') or ''}<br/>{proveedor.get('street') or ''}, "
                  f"{proveedor.get('city') or ''}<br/>{proveedor.get('phone') or ''} · "
                  f"{proveedor.get('email') or ''}", TEXTO),
        Paragraph("<font size=15 color='#C8102E'><b>FACTURA</b></font><br/>"
                  "<font size=8>Documento Tributario Electrónico (FEL)</font><br/>"
                  f"<b>Serie:</b> {serie} &nbsp; <b>Número:</b> {numero}<br/>"
                  f"<b>Fecha de emisión:</b> {fecha_larga(factura['invoice_date'])}", DERECHA),
    ]], colWidths=[105 * mm, 75 * mm])
    emisor.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("BOX", (1, 0), (1, 0), 1, ROJO),
                                ("LEFTPADDING", (1, 0), (1, 0), 8)]))
    historia += [emisor, Spacer(1, 8)]
    receptor = Table([[Paragraph(f"<b>Receptor:</b> {QUETZALMART['nombre']} &nbsp;&nbsp; <b>NIT:</b> "
                                 f"{QUETZALMART['nit']}<br/><b>Dirección:</b> {QUETZALMART['direccion']}<br/>"
                                 f"<b>Orden de compra:</b> {factura.get('invoice_origin') or ''}", TEXTO)]],
                     colWidths=[180 * mm])
    receptor.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CREMA),
                                  ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E9DDBB"))]))
    historia += [receptor, Spacer(1, 8)]
    filas = [["Cant.", "Descripción", "Precio unitario", "Subtotal"]]
    for linea in lineas:
        filas.append([f"{linea['quantity']:g}", Paragraph(linea["name"], CELDA),
                      quetzales(linea["price_unit"]), quetzales(linea["price_subtotal"])])
    filas += [["", "", "Subtotal", quetzales(factura["amount_untaxed"])],
              ["", "", "IVA (12 %)", quetzales(factura["amount_tax"])],
              ["", "", "TOTAL", quetzales(factura["amount_total"])]]
    tabla = Table(filas, colWidths=[16 * mm, 104 * mm, 30 * mm, 30 * mm], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERDE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"), ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("LINEBELOW", (0, 1), (-1, -4), 0.3, colors.HexColor("#DDE5E0")),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"), ("TEXTCOLOR", (2, -1), (-1, -1), VERDE_OSCURO),
        ("LINEABOVE", (2, -3), (-1, -3), 0.8, VERDE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    historia += [tabla, Spacer(1, 6),
                 Paragraph(f"<b>Total en letras:</b> {numero_a_letras(factura['amount_total'])}", TEXTO),
                 Paragraph("Sujeto a pagos trimestrales ISR. Condición de pago: crédito 30 días.", TEXTO),
                 Spacer(1, 10),
                 Paragraph(f"<b>Número de autorización:</b> {autorizacion}<br/>"
                           "<b>Certificador:</b> Certificadora Digital Centroamericana, S.A. · "
                           "NIT 7701223-4", PEQUENO)]
    return construir(ruta, historia)


# ---------------------------------------------------------------------------
def contrato_outsourcing(carpeta, numero, socio, servicio, monto):
    inicio = date(2026, 1, 1 + (numero - 1) * 3)
    codigo = f"QM-OUT-2026-{numero:03d}"
    ruta = Path(carpeta) / f"Contrato outsourcing {codigo} - {socio['name']}.pdf"
    historia = []
    encabezado_quetzalmart(historia, "CONTRATO DE PRESTACIÓN DE SERVICIOS TERCERIZADOS",
                           f"Contrato número {codigo}")
    historia.append(Paragraph(
        f"En la Ciudad de Guatemala, el {fecha_larga(inicio)}, comparecen por una parte "
        f"<b>{QUETZALMART['representante']}</b>, en su calidad de {QUETZALMART['cargo']} de "
        f"<b>{QUETZALMART['nombre']}</b>, NIT {QUETZALMART['nit']}, en adelante «EL CONTRATANTE»; y por la "
        f"otra parte el representante legal de <b>{socio['name']}</b>, NIT {socio.get('vat') or ''}, con "
        f"domicilio en {socio.get('street') or ''}, {socio.get('city') or ''}, en adelante «EL PROVEEDOR». "
        "Ambas partes aseguran hallarse en el libre ejercicio de sus derechos civiles y convienen en "
        "celebrar el presente contrato de conformidad con las cláusulas siguientes:", TEXTO))
    mensual_iva = monto * 1.12
    clausulas(historia, [
        ("OBJETO", f"EL PROVEEDOR se obliga a prestar a EL CONTRATANTE el servicio de <b>{servicio.lower()}</b> "
                   "en las sucursales de Guatemala, México y El Salvador, con su propio personal, equipo y "
                   "herramientas, bajo su exclusiva dirección y responsabilidad."),
        ("ALCANCE Y NIVELES DE SERVICIO", "El servicio se prestará según el plan de trabajo anexo, con un "
                   "cumplimiento mínimo del 98 % de las visitas programadas. EL PROVEEDOR entregará un informe "
                   "mensual de actividades que será archivado en el gestor documental de EL CONTRATANTE."),
        ("PLAZO", f"El plazo es de doce (12) meses contados a partir del {fecha_larga(inicio)}, prorrogable "
                  "por períodos iguales mediante acuerdo escrito con treinta días de anticipación."),
        ("HONORARIOS", f"EL CONTRATANTE pagará la cantidad mensual de <b>{quetzales(monto)}</b> más el "
                       f"Impuesto al Valor Agregado, para un total de {quetzales(mensual_iva)} "
                       f"({numero_a_letras(mensual_iva)}), contra entrega de la factura electrónica (FEL)."),
        ("FORMA DE PAGO", "Los pagos se realizarán por transferencia bancaria dentro de los treinta (30) días "
                          "siguientes a la recepción de la factura y del informe mensual aprobado."),
        ("RELACIÓN LABORAL", "EL PROVEEDOR es el único patrono del personal que asigne al servicio y asume "
                             "todas las obligaciones laborales, de seguridad social (IGSS) y de salud ocupacional. "
                             "No existe relación laboral entre dicho personal y EL CONTRATANTE."),
        ("CONFIDENCIALIDAD", "EL PROVEEDOR guardará reserva sobre la información comercial, de clientes y de "
                             "inventarios a la que tenga acceso, aun después de terminado el contrato."),
        ("SEGUROS Y RESPONSABILIDAD", "EL PROVEEDOR mantendrá vigente un seguro de responsabilidad civil por un "
                                      "monto no menor de Q 250,000.00 que cubra daños a personas o bienes."),
        ("TERMINACIÓN", "Cualquiera de las partes podrá dar por terminado el contrato con aviso escrito de "
                        "treinta días, o de inmediato si la otra parte incumple sus obligaciones esenciales."),
        ("JURISDICCIÓN", "Para cualquier controversia, las partes se someten a los tribunales de la Ciudad de "
                         "Guatemala y señalan como lugar para recibir notificaciones sus direcciones indicadas."),
    ])
    historia.append(Paragraph("Leído lo escrito y enteradas de su contenido, objeto, validez y efectos legales, "
                              "las partes lo aceptan, ratifican y firman.", TEXTO))
    firmas(historia, f"{QUETZALMART['representante']}<br/>EL CONTRATANTE",
           f"Representante legal<br/>{socio['name']}<br/>EL PROVEEDOR")
    return construir(ruta, historia)


# ---------------------------------------------------------------------------
def contrato_laboral(carpeta, contrato, empleado):
    nombre = empleado["name"]
    puesto = contrato["job_id"][1] if contrato.get("job_id") else ""
    departamento = contrato["department_id"][1] if contrato.get("department_id") else ""
    sucursal = empleado["work_location_id"][1] if empleado.get("work_location_id") else "Sucursal Guatemala"
    codigo = f"QM-RH-{contrato['id']:04d}"
    ruta = Path(carpeta) / f"Contrato laboral {codigo} - {nombre}.pdf"
    historia = []
    encabezado_quetzalmart(historia, "CONTRATO INDIVIDUAL DE TRABAJO",
                           f"Registro {codigo} · Artículo 29 del Código de Trabajo de Guatemala")
    datos = [
        ["Nombre del trabajador", nombre],
        ["Documento de identificación (DPI)", empleado.get("identification_id") or ""],
        ["Puesto", puesto],
        ["Departamento", departamento],
        ["Lugar de prestación del servicio", sucursal],
        ["Fecha de inicio de la relación laboral", fecha_larga(contrato["date_start"])],
        ["Salario mensual", f"{quetzales(contrato['wage'])} ({numero_a_letras(contrato['wage'])})"],
        ["Correo de trabajo", empleado.get("work_email") or ""],
    ]
    tabla = Table([[Paragraph(f"<b>{a}</b>", CELDA), Paragraph(str(b), CELDA)] for a, b in datos],
                  colWidths=[62 * mm, 118 * mm])
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), CREMA),
                               ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2D8B8")),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    historia += [Paragraph(
        f"<b>{QUETZALMART['nombre']}</b>, en adelante «EL EMPLEADOR», representada por "
        f"{QUETZALMART['representante']}, y <b>{nombre}</b>, en adelante «EL TRABAJADOR», celebran el "
        "presente contrato individual de trabajo por tiempo indefinido, con los datos siguientes:", TEXTO),
        tabla, Spacer(1, 6)]
    clausulas(historia, [
        ("SERVICIOS", f"EL TRABAJADOR desempeñará el puesto de <b>{puesto}</b> y las funciones descritas en el "
                      "manual de puestos de QuetzalMart, con la diligencia y eficiencia debidas."),
        ("JORNADA", "La jornada ordinaria es diurna, de ocho horas diarias y cuarenta y cuatro horas semanales, "
                    "en turnos rotativos entre las 7:00 y las 21:00 horas, con un día de descanso semanal."),
        ("SALARIO Y FORMA DE PAGO", f"El salario mensual es de {quetzales(contrato['wage'])}, pagadero en dos "
                    "quincenas por depósito bancario. Además, EL TRABAJADOR recibirá la bonificación incentivo "
                    "de Q 250.00 mensuales establecida en el Decreto 37-2001."),
        ("PRESTACIONES", "EL TRABAJADOR gozará de aguinaldo, Bono 14, vacaciones de quince días hábiles por año "
                         "laborado, afiliación al IGSS y demás prestaciones que establece la ley."),
        ("PERÍODO DE PRUEBA", "Los primeros dos meses se consideran período de prueba, durante el cual cualquiera "
                              "de las partes puede terminar el contrato sin responsabilidad."),
        ("CONFIDENCIALIDAD", "EL TRABAJADOR guardará reserva de la información comercial, de precios, clientes "
                             "y proveedores de EL EMPLEADOR."),
        ("LEGISLACIÓN APLICABLE", "En lo no previsto, este contrato se rige por el Código de Trabajo, el "
                                  "Reglamento Interior de Trabajo de QuetzalMart y demás leyes laborales."),
    ])
    historia.append(Paragraph(f"Firmado en la Ciudad de Guatemala, el {fecha_larga(contrato['date_start'])}.",
                              TEXTO))
    firmas(historia, f"{QUETZALMART['representante']}<br/>EL EMPLEADOR", f"{nombre}<br/>EL TRABAJADOR")
    return construir(ruta, historia)


if __name__ == "__main__":
    # Vista previa sin Odoo: un documento de cada tipo con datos de ejemplo.
    salida = Path(__file__).resolve().parent / "vista_previa"
    salida.mkdir(exist_ok=True)
    factura_proveedor(salida, {"ref": "FEL-PRV-001-00001", "invoice_date": "2026-08-14",
                               "amount_untaxed": 1000, "amount_tax": 120, "amount_total": 1120,
                               "invoice_origin": "P00001"},
                      {"name": "Distribuidora de Granos El Altiplano, S.A.", "vat": "1234560-7",
                       "street": "Zona industrial, bodega 4", "city": "Ciudad de Guatemala"},
                      [{"name": "[DES-001] Arroz blanco grano largo 2 lb", "quantity": 100, "price_unit": 7.1,
                        "price_subtotal": 710.0},
                       {"name": "[DES-002] Frijol negro entero 2 lb", "quantity": 34.5, "price_unit": 8.4,
                        "price_subtotal": 290.0}])
    contrato_outsourcing(salida, 1, {"name": "Seguridad Privada Centinela, S.A.", "vat": "4455667-1",
                                     "street": "Oficinas centrales, nivel 8", "city": "Ciudad de Guatemala"},
                         "Vigilancia y monitoreo de las tres sucursales", 18500.0)
    contrato_laboral(salida, {"id": 2, "job_id": [1, "Gerente de Sucursal"],
                              "department_id": [1, "Operaciones de Tienda"], "date_start": "2024-03-04",
                              "wage": 11650.0},
                     {"name": "Rodrigo Esteban Monterroso Paz", "identification_id": "2547896310101",
                      "work_location_id": [1, "Sucursal Guatemala"],
                      "work_email": "rodrigo.monterroso@quetzalmart.example"})
    print("Vista previa en", salida)
