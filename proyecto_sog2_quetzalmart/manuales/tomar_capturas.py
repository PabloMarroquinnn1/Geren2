"""Toma las capturas de pantalla de Odoo y de la tienda para los manuales.

Ejecútelo contra su servidor en la nube cuando los datos ya estén cargados:

    pip install playwright && playwright install chromium
    python manuales/tomar_capturas.py --url https://SU-DOMINIO --clave CLAVE_ADMIN

Las imágenes quedan en manuales/capturas/ con los nombres que usan manual_1.md y manual_3.md.
"""
import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import Error as ErrorPlaywright
from playwright.sync_api import sync_playwright

SALIDA = Path(__file__).resolve().parent / "capturas"
RAIZ = Path(__file__).resolve().parents[1]

# nombre, ruta de Odoo, vista (lista/kanban/None), hacer clic en el primer registro
CAPTURAS_ODOO = [
    ("01_aplicaciones", "/odoo/orders", "menu", False),
    ("02_ventas_pedidos", "/odoo/orders", "list", False),
    ("03_venta_detalle", "/odoo/orders", "list", True),
    ("04_ventas_cotizaciones", "/odoo/sales", "list", False),
    ("05_compras_ordenes", "/odoo/purchase-orders", "list", False),
    ("06_compra_detalle", "/odoo/purchase-orders", "list", True),
    ("07_facturas_clientes", "/odoo/customer-invoices", "list", False),
    ("08_factura_detalle", "/odoo/customer-invoices", "list", True),
    ("09_facturas_proveedor", "/odoo/vendor-bills", "list", False),
    ("10_empleados", "/odoo/employees", "kanban", False),
    ("11_empleado_detalle", "/odoo/employees", "list", True),
    ("12_departamentos", "/odoo/departments", "kanban", False),
    ("13_puestos", "/odoo/action-hr.action_hr_job", "list", False),
    ("14_contratos", "/odoo/employee-contracts", "list", False),
    ("15_crm_flujo", "/odoo/crm", "kanban", False),
    ("16_contactos", "/odoo/contacts", "kanban", False),
    ("17_productos", "/odoo/products", "kanban", False),
    ("18_producto_detalle", "/odoo/products", "list", True),
    ("19_inventario_por_ubicacion", "/odoo/action-stock.dashboard_open_quants", "list", False),
    ("20_almacenes", "/odoo/action-stock.action_warehouse_form", "list", False),
    ("21_documentos_carpetas", "/odoo/action-dms.action_dms_directory", "kanban", False),
    ("22_documentos_archivos", "/odoo/action-dms.action_dms_file", "list", False),
    ("23_marketing_campanas", "/odoo/email-marketing", "list", False),
    ("24_marketing_campana_detalle", "/odoo/email-marketing", "kanban", True),
]


def iniciar_sesion(pagina, url, usuario, clave):
    pagina.goto(url + "/web/login")
    pagina.fill("input[name=login]", usuario)
    pagina.fill("input[name=password]", clave)
    pagina.click(".oe_login_form button[type=submit]")
    pagina.wait_for_url(re.compile(r"/odoo"), timeout=60000)


VISTA_LISTA = ".o_action_manager .o_view_controller, .o_home_menu, .o_action_manager .o_kanban_view"


def capturar_odoo(pagina, url, nombre, ruta, vista, abrir_primero):
    # El backend de Odoo mantiene abierto su canal en tiempo real: se espera a
    # que aparezca la vista en lugar de esperar a que la red quede inactiva.
    pagina.goto(url + ruta)
    pagina.wait_for_selector(VISTA_LISTA, timeout=30000)
    pagina.wait_for_timeout(1500)
    if vista == "menu":
        pagina.click(".o_navbar_apps_menu button")
        pagina.wait_for_timeout(1000)
    elif vista:
        boton = pagina.locator(f".o_switch_view.o_{vista}")
        if boton.count():
            boton.first.click()
            pagina.wait_for_selector(f".o_{vista}_view", timeout=20000)
            pagina.wait_for_timeout(1000)
    if abrir_primero:
        filas = pagina.locator(".o_data_row td.o_data_cell[name='name'], .o_data_row td.o_data_cell[name='subject']")
        if not filas.count():
            filas = pagina.locator(".o_data_row td.o_data_cell, .o_kanban_record")
        filas.first.click()
        pagina.wait_for_selector(".o_form_view", timeout=20000)
        pagina.wait_for_timeout(1200)
    pagina.screenshot(path=str(SALIDA / f"{nombre}.png"))


def capturar_importacion(pagina, url):
    """Pantalla de importación con la plantilla de clientes después de 'Probar' (sin importar)."""
    pagina.goto(url + "/odoo/contacts/import?active_model=res.partner")
    pagina.wait_for_selector("button.o_import_file", timeout=30000)
    pagina.screenshot(path=str(SALIDA / "25_importar_inicio.png"))
    with pagina.expect_file_chooser() as selector:
        pagina.click("button.o_import_file")
    selector.value.set_files(str(RAIZ / "carga_masiva" / "plantillas" / "05_clientes.xlsx"))
    pagina.wait_for_selector("button:has-text('Probar')", timeout=30000)
    pagina.wait_for_timeout(1000)
    pagina.screenshot(path=str(SALIDA / "26_importar_columnas.png"))
    pagina.click("button:has-text('Probar')")
    pagina.wait_for_timeout(2500)
    pagina.screenshot(path=str(SALIDA / "27_importar_prueba.png"))


def capturar_tienda(navegador, url, sin_verificar_ssl=False):
    contexto = navegador.new_context(viewport={"width": 1440, "height": 900},
                                     ignore_https_errors=sin_verificar_ssl)
    pagina = contexto.new_page()
    pagina.goto(url + "/", wait_until="networkidle")
    pagina.screenshot(path=str(SALIDA / "30_tienda_inicio.png"), full_page=True)
    pagina.goto(url + "/shop", wait_until="networkidle")
    pagina.screenshot(path=str(SALIDA / "31_tienda_catalogo.png"))
    pagina.locator(".oe_product a.oe_product_image_link").first.click()
    pagina.wait_for_selector("#add_to_cart")
    pagina.wait_for_timeout(800)
    pagina.screenshot(path=str(SALIDA / "32_tienda_producto.png"))
    pagina.click("#add_to_cart")
    pagina.wait_for_timeout(1500)
    pagina.goto(url + "/shop/cart", wait_until="networkidle")
    pagina.screenshot(path=str(SALIDA / "33_tienda_carrito.png"))
    contexto.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True)
    parser.add_argument("--usuario", default="admin@quetzalmart.com")
    parser.add_argument("--clave", required=True)
    parser.add_argument("--sin-verificar-ssl", action="store_true", help="Solo para pruebas locales")
    args = parser.parse_args()
    url = args.url.rstrip("/")
    SALIDA.mkdir(exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900}, locale="es-GT",
                                         ignore_https_errors=args.sin_verificar_ssl)
        pagina = contexto.new_page()
        iniciar_sesion(pagina, url, args.usuario, args.clave)
        fallas = 0
        for nombre, ruta, vista, abrir in CAPTURAS_ODOO:
            try:
                capturar_odoo(pagina, url, nombre, ruta, vista, abrir)
                print("  ok   ", nombre)
            except ErrorPlaywright as error:
                fallas += 1
                print("  falla", nombre, str(error).splitlines()[0][:90])
        for paso in (lambda: capturar_importacion(pagina, url),
                     lambda: capturar_tienda(navegador, url, args.sin_verificar_ssl)):
            try:
                paso()
            except ErrorPlaywright as error:
                fallas += 1
                print("  falla", str(error).splitlines()[0][:90])
        navegador.close()
    print(f"Capturas en {SALIDA} ({fallas} con problemas)")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
