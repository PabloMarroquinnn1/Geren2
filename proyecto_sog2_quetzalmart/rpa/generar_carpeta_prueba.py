"""Crea una carpeta de prueba para el robot con la estructura que describe el enunciado.

Carpetas "clientes - ...", "proveedores - ...", "reclamos - ...", "registro - ..." y
"productos - ..." con libros de Excel de varias hojas. Las hojas que interesan
("clientes" y "productos") van en la 5.a posición; hay además casos difíciles:
encabezados en español o con asterisco, filas vacías, duplicados, un libro de una
sola hoja (como los de ejemplo del auxiliar), archivos sin hojas útiles, un
archivo temporal de Excel (~$) y un .txt que deben ignorarse.

Uso:  python rpa/generar_carpeta_prueba.py [carpeta_destino]
"""
import sys
from pathlib import Path

from openpyxl import Workbook

DESTINO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "carpeta_prueba"

CLIENTES_EN = ["Name*", "Company Type*", "Related Company", "Email", "Phone", "Street", "Street2", "City",
               "State", "Zip", "Country", "Tax ID", "Website", "Tags", "Reference", "Notes"]
CLIENTES_ES = ["Nombre", "Tipo de compañía", "Empresa relacionada", "Correo electrónico", "Teléfono",
               "Calle", "Calle 2", "Ciudad", "Estado", "Código postal", "País", "NIT", "Sitio web",
               "Etiquetas", "Referencia", "Notas"]
PRODUCTOS = ["ID Externo", "Name", "Product Type", "Internal Reference", "Barcode", "Sales Price", "Cost",
             "Weight", "Sales Description", "Product Values", "Cantidad a la mano", "Está publicado"]

RELLENO = {
    "proveedor": [["Proveedor", "NIT", "Contacto"], ["Distribuidora Central", "1234567-8", "Ana Pérez"]],
    "reclamos": [["Fecha", "Cliente", "Motivo"], ["2026-10-01", "Tienda La Fe", "Producto golpeado"]],
    "registros": [["Fecha", "Caja", "Total"], ["2026-10-02", "Caja 1", 1520.75]],
    "resumen": [["Indicador", "Valor"], ["Ventas del mes", 48200]],
    "notas": [["Nota"], ["Revisar precios de temporada"]],
}


def libro(ruta, hojas):
    """hojas: lista de (nombre, filas). La primera fila de cada hoja es el encabezado."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    for nombre, filas in hojas:
        hoja = wb.create_sheet(nombre)
        for fila in filas:
            hoja.append(fila)
    wb.save(ruta)
    print("  ", ruta.relative_to(DESTINO))


def con_relleno(objetivo, filas, nombre_objetivo):
    """Libro de 6 hojas con la hoja objetivo en la 5.a posición."""
    orden = ["proveedor", "reclamos", "registros", "resumen"]
    return [(n, RELLENO[n]) for n in orden] + [(nombre_objetivo, filas), ("notas", RELLENO["notas"])]


def main():
    print("Carpeta de prueba:", DESTINO)
    # --- clientes -------------------------------------------------------------
    libro(DESTINO / "clientes - cartera Guatemala" / "clientes - mayoristas zona 4.xlsx", con_relleno(
        "clientes", [CLIENTES_EN,
                     ["RPA Comercial Los Altos", "Company", None, "compras@losaltos.example", "+502 2245 1100",
                      "4a. Avenida 10-25", "Zona 4", "Ciudad de Guatemala", "Guatemala", "01004", "Guatemala",
                      "7458123-1", "https://losaltos.example", "Mayorista, RPA 2026", "RPA-C-001",
                      "Compra semanal de abarrotes"],
                     ["RPA Lucía Estrada", "Individual", "RPA Comercial Los Altos", "lucia.estrada@losaltos.example",
                      "+502 5512 7788", "4a. Avenida 10-25", None, "Ciudad de Guatemala", "Guatemala", "01004",
                      "GT", None, None, "Contacto de compras", "RPA-C-002", None],
                     [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                     ["RPA Hotel Volcán de Fuego", "Company", None, "reservas@volcanfuego.example", "+502 7832 4400",
                      "Calle del Arco 8", None, "Antigua Guatemala", "Sacatepéquez", "03001", "Guatemala",
                      "6623145-9", None, "Hotelería; RPA 2026", "RPA-C-003", None]],
        "clientes"))
    libro(DESTINO / "clientes - cartera Guatemala" / "clientes - registros web octubre.xlsx", con_relleno(
        "clientes", [CLIENTES_ES,
                     ["RPA Andrea Pineda", "Persona", None, "andrea.pineda@correo.example", "5590 1234",
                      "Colonia El Maestro", None, "Mixco", "Guatemala", 1057, "Guatemala", "CF", None,
                      "Registro web", "RPA-C-004", "Se registró en la tienda en línea"],
                     ["RPA Comercial Los Altos", "Compañía", None, "compras@losaltos.example", None, None, None,
                      None, None, None, None, None, None, None, "RPA-C-001", "Duplicado: debe omitirse"]],
        "Clientes "))
    libro(DESTINO / "clientes - cartera México y El Salvador" / "clientes - Tapachula.xlsx", con_relleno(
        "clientes", [CLIENTES_EN,
                     ["RPA Abarrotes El Soconusco", "Company", None, "ventas@soconusco.example", "+52 962 625 1100",
                      "Avenida Central Norte 14", None, "Tapachula", "Chiapas", "30700", "Mexico", "ASO120304AB1",
                      None, "Mayorista", "RPA-C-005", None]],
        "clientes"))
    libro(DESTINO / "clientes - cartera México y El Salvador" / "clientes - archivo 2025" /
          "clientes - Santa Ana historico.xlsx", con_relleno(
        "clientes", [CLIENTES_EN,
                     ["RPA Pupusería Doña Tere", "Company", None, "pedidos@donatere.example", "+503 2440 8899",
                      "Calle Libertad Oriente 7", None, "Santa Ana", None, "02101", "El Salvador",
                      "0210-120588-101-2", None, "Restaurante", "RPA-C-006", None]],
        "clientes"))
    # --- productos ------------------------------------------------------------
    libro(DESTINO / "productos - temporada fin de año" / "productos - nuevos lanzamientos.xlsx", con_relleno(
        "productos", [PRODUCTOS,
                      ["rpa_tamal_colorado", "RPA Tamal colorado congelado 6 unidades", "Goods", "RPA-001",
                       7401234567895, "58.00", "39.50", 1.2, "Tamal chapín listo para calentar", None, 40, "True"],
                      ["rpa_ponche_frutas", "RPA Ponche de frutas 1 L", "Goods", "RPA-002", None, 24.5, 16, 1.05,
                       "Ponche navideño con frutas de temporada", "Sabor: piña, manzana, ciruela", "35", "Sí"],
                      ["rpa_envio_express", "RPA Servicio de envío express", "Service", None, None, 35, 20, None,
                       "Entrega en menos de 3 horas", None, 75, "False"],
                      [None, None, None, None, None, None, None, None, None, None, None, None]],
        "productos"))
    libro(DESTINO / "productos - temporada fin de año" / "productos - marca propia.xlsx", con_relleno(
        "productos", [PRODUCTOS,
                      ["", "RPA Chocolate de mesa artesanal 500 g", "Goods", "RPA-003", "7401234567901", "Q 32.90",
                       "21,40", 0.5, "Chocolate de mesa de Cobán", None, 60, "TRUE"]],
        "productos"))
    # Libro de una sola hoja (como los archivos de ejemplo del auxiliar).
    libro(DESTINO / "productos - temporada fin de año" / "productos - una sola hoja.xlsx",
          [("productos", [PRODUCTOS,
                          ["rpa_pan_dulce", "RPA Pan dulce navideño 450 g", "Goods", "RPA-004", None, 27, 15.25,
                           0.45, "Pan dulce con pasas y nueces", None, 25, 1]])])
    # --- carpetas sin información de interés ---------------------------------
    libro(DESTINO / "proveedores - nacionales" / "proveedores - listado 2026.xlsx",
          [(n, f) for n, f in RELLENO.items()])
    libro(DESTINO / "reclamos - quejas sucursales" / "reclamos - octubre.xlsx",
          [("reclamos", RELLENO["reclamos"]), ("resumen", RELLENO["resumen"])])
    libro(DESTINO / "registro - ventas diarias" / "registro - caja 1.xlsx",
          [("registros", RELLENO["registros"]), ("notas", RELLENO["notas"])])
    basura = DESTINO / "registro - ventas diarias" / "~$registro - caja 1.xlsx"
    basura.write_bytes(b"archivo temporal de Excel")
    (DESTINO / "registro - ventas diarias" / "leeme.txt").write_text("No es un Excel.", encoding="utf-8")
    print("   (más un archivo temporal ~$ y un .txt que el robot debe ignorar)")


if __name__ == "__main__":
    main()
