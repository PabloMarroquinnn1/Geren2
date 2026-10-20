"""Genera visitas de prueba en la tienda de QuetzalMart para que GA4 tenga datos.

El enunciado pide "generar interacciones para que se puedan ver datos". Este script
abre un navegador real (Chromium con Playwright) y recorre la tienda como lo haría
un cliente: cada visita es un usuario nuevo (cookies nuevas) que llega desde una
campaña distinta (utm_source / utm_medium / utm_campaign) y sigue uno de estos
recorridos:

  * explorador ............ ve la portada, una categoría y algunos productos
  * carrito_abandonado .... agrega al carrito y se va (alimenta el abandono)
  * pago_abandonado ....... llega al pago (begin_checkout) y no termina
  * comprador ............. compra completa con el pago de prueba (purchase)

Las compras de prueba quedan registradas en Odoo (pedidos y facturas reales del
entorno de pruebas). Complementen estos datos navegando también a mano.

Uso:
    pip install playwright && playwright install chromium
    python analytics/simular_trafico.py --url https://SU-DOMINIO --visitas 40
    python analytics/simular_trafico.py --url ... --visitas 10 --ver   (con ventana)
"""
import argparse
import random
import re
import time

from playwright.sync_api import TimeoutError as TiempoAgotado
from playwright.sync_api import sync_playwright

# Navegador de escritorio común (GA4 descarta tráfico que se identifica como robot).
AGENTE = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

CAMPANAS = [
    # utm_source, utm_medium, utm_campaign, peso
    ("facebook", "social", "temporada_quetzalmart", 5),
    ("instagram", "social", "temporada_quetzalmart", 3),
    ("google", "cpc", "busqueda_supermercado", 4),
    ("correo_postcompra", "email", "temporada_quetzalmart", 3),
    ("campana_correo", "email", "temporada_quetzalmart", 2),
    (None, None, None, 4),  # tráfico directo
]
RECORRIDOS = [("explorador", 4), ("carrito_abandonado", 3), ("pago_abandonado", 2), ("comprador", 3)]
NOMBRES = ["Ana", "Luis", "Carla", "Jorge", "Sofía", "Diego", "María", "Pedro", "Lucía", "Andrés",
           "Valeria", "Kevin", "Gabriela", "Óscar", "Daniela", "Erick"]
APELLIDOS = ["López", "Pérez", "Ramírez", "Castillo", "Méndez", "Ajú", "Morales", "Rivas", "Cruz", "Toledo"]
DESTINOS = [
    ("Guatemala", "Ciudad de Guatemala", "01010", "+502 5{:03d} {:04d}"),
    ("Guatemala", "Quetzaltenango", "09001", "+502 4{:03d} {:04d}"),
    ("México", "Tapachula", "30700", "+52 962 {:03d} {:04d}"),
    ("El Salvador", "Santa Ana", "02101", "+503 7{:03d} {:04d}"),
]


def elegir(opciones):
    return random.choices(opciones, weights=[o[-1] for o in opciones])[0]


def pausa(minimo=0.8, maximo=2.5):
    time.sleep(random.uniform(minimo, maximo))


def abrir_producto(pagina, base):
    pagina.goto(base + "/shop", wait_until="networkidle")
    tarjetas = pagina.locator(".oe_product a.oe_product_image_link")
    tarjetas.nth(random.randrange(tarjetas.count())).click()
    pagina.wait_for_selector("#add_to_cart", timeout=20000)
    pausa(1.5, 4)


def agregar_al_carrito(pagina):
    mas = pagina.locator(".css_quantity a.js_add_cart_json:has(.fa-plus)")
    for _ in range(random.choice([0, 0, 1, 2])):
        if mas.count():
            mas.first.click()
            pausa(0.3, 0.8)
    pagina.click("#add_to_cart")
    pausa(1.5, 3)


def explorar(pagina, base):
    categorias = pagina.locator("a[href*='/shop/category/']")
    if categorias.count():
        categorias.nth(random.randrange(categorias.count())).click()
        pagina.wait_for_load_state("networkidle")
        pausa()
    for _ in range(random.randint(1, 3)):
        abrir_producto(pagina, base)


CORREO_BASE = None  # --correo-base


def correo_de_visita(numero):
    """Con --correo-base usa alias (su.correo+visita3@gmail.com) para que nada rebote."""
    marca = f"visita{numero}.{int(time.time())}"
    if CORREO_BASE and "@" in CORREO_BASE:
        usuario, dominio = CORREO_BASE.split("@")
        return f"{usuario}+{marca}@{dominio}"
    return f"{marca}@correo.example"


def llenar_direccion(pagina, numero):
    pais, ciudad, cp, telefono = random.choice(DESTINOS)
    nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
    pagina.fill("input[name=email]", correo_de_visita(numero))
    pagina.fill("input[name=name]", nombre)
    pagina.fill("input[name=phone]", telefono.format(random.randint(100, 999), random.randint(1000, 9999)))
    pagina.fill("input[name=street]", f"{random.randint(1, 30)}a. Avenida {random.randint(1, 40)}-{random.randint(10, 90)}")
    pagina.fill("input[name=city]", ciudad)
    pagina.fill("input[name=zip]", cp)
    pagina.select_option("select[name=country_id]", label=pais)
    pausa(0.8, 1.2)
    estado = pagina.locator("select[name=state_id]")
    if estado.count() and estado.is_visible():
        opciones = estado.locator("option").all_inner_texts()[1:]
        if opciones:
            pagina.select_option("select[name=state_id]", label=random.choice(opciones))
    pagina.click("#save_address")
    pagina.wait_for_url(re.compile(r"/shop/(checkout|payment)"), timeout=30000)
    pagina.wait_for_load_state("networkidle")


def ir_a_pagar(pagina, base, numero):
    """Carrito -> dirección -> método de entrega -> página de pago."""
    pagina.goto(base + "/shop/cart", wait_until="networkidle")
    pausa()
    pagina.click("a[name='website_sale_main_button']")
    pagina.wait_for_url(re.compile(r"/shop/(address|checkout|payment)"), timeout=30000)
    pagina.wait_for_load_state("networkidle")
    if "/shop/address" in pagina.url:
        llenar_direccion(pagina, numero)
    if "/shop/checkout" in pagina.url:
        pausa()
        pagina.click("a[name='website_sale_main_button']")
        pagina.wait_for_url("**/shop/payment**", timeout=30000)
        pagina.wait_for_load_state("networkidle")


def visita(navegador, base, numero):
    fuente, medio, campana, _ = elegir(CAMPANAS)
    recorrido = elegir(RECORRIDOS)[0]
    contexto = navegador.new_context(user_agent=AGENTE, locale="es-GT",
                                     viewport={"width": random.choice([1366, 1440, 1536, 390]),
                                               "height": random.choice([768, 900, 844])})
    pagina = contexto.new_page()
    entrada = base + "/"
    if fuente:
        entrada += f"?utm_source={fuente}&utm_medium={medio}&utm_campaign={campana}"
    try:
        pagina.goto(entrada, wait_until="networkidle")
        pausa(2, 4)
        explorar(pagina, base)
        if recorrido != "explorador":
            agregar_al_carrito(pagina)
            if random.random() < 0.4:
                abrir_producto(pagina, base)
                agregar_al_carrito(pagina)
        if recorrido in ("pago_abandonado", "comprador"):
            ir_a_pagar(pagina, base, numero)
        if recorrido == "comprador":
            pausa()
            pagina.click("button[name='o_payment_submit_button']")
            pagina.wait_for_url("**/shop/confirmation**", timeout=60000)
            pagina.wait_for_load_state("networkidle")
            pausa(3, 5)  # deja tiempo a que GA4 envíe "purchase"
            estado = "compra confirmada"
        else:
            pausa(2, 3)
            estado = "ok (" + pagina.url.split("?")[0].replace(base, "") + ")"
    except TiempoAgotado as error:
        estado = f"incompleta ({error.message.splitlines()[0][:60]})"
    finally:
        contexto.close()
    print(f"  visita {numero:>3}: {fuente or 'directo':<18} {recorrido:<19} {estado}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="https://su-dominio (sin / al final)")
    parser.add_argument("--visitas", type=int, default=30)
    parser.add_argument("--ver", action="store_true", help="Mostrar la ventana del navegador")
    parser.add_argument("--semilla", type=int, help="Para repetir exactamente la misma simulación")
    parser.add_argument("--correo-base", help="Correo propio para los compradores simulados (se usan alias +visitaN)")
    args = parser.parse_args()
    global CORREO_BASE
    CORREO_BASE = args.correo_base
    if args.semilla is not None:
        random.seed(args.semilla)
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=not args.ver)
        print(f"Simulando {args.visitas} visitas en {args.url}")
        for numero in range(1, args.visitas + 1):
            visita(navegador, args.url.rstrip("/"), numero)
        navegador.close()
    print("Listo. Los datos aparecen en GA4 > Tiempo real de inmediato y en los informes en 24-48 h.")


if __name__ == "__main__":
    main()
