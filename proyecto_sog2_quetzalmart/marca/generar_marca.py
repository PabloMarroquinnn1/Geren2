"""Genera la identidad visual de QuetzalMart: logo, portadas, categorías y productos.

Las imágenes se dibujan con HTML/CSS y se fotografían con Chromium (Playwright),
así todo el material gráfico es original del proyecto.

Uso:
    pip install playwright openpyxl && playwright install chromium
    python marca/generar_marca.py            # todo
    python marca/generar_marca.py productos  # solo una parte
"""
import colorsys
import html
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "carga_masiva"))
import catalogo  # noqa: E402

ADDON_IMPL = RAIZ / "odoo_addons" / "qm_implementacion" / "static"
ADDON_CRM = RAIZ / "odoo_addons" / "qm_crm_postventa" / "static"
SALIDA_PRODUCTOS = RAIZ / "carga_masiva" / "imagenes" / "productos"

VERDE = "#0B6E4F"
VERDE_OSCURO = "#064635"
VERDE_CLARO = "#1BAA6B"
ROJO = "#C8102E"
DORADO = "#F2B705"
CREMA = "#FFF8E7"

FUENTES = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700'
    '&family=Nunito:wght@600;700;800&display=swap" rel="stylesheet">'
)

# Quetzal estilizado (cuerpo verde, pecho rojo, cola larga) dentro de un círculo.
QUETZAL_SVG = f"""
<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="60" r="57" fill="{VERDE}"/>
  <circle cx="60" cy="60" r="51" fill="none" stroke="{DORADO}" stroke-width="2.5"/>
  <path d="M52 74 C62 92 74 104 96 110" stroke="{VERDE_CLARO}" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M56 72 C68 86 80 94 102 96" stroke="#7FE0B0" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M50 76 C56 94 62 104 78 116" stroke="#159A60" stroke-width="5" fill="none" stroke-linecap="round"/>
  <ellipse cx="54" cy="58" rx="17" ry="23" transform="rotate(-18 54 58)" fill="{VERDE_CLARO}"/>
  <path d="M44 62 C44 76 54 82 64 76 C60 70 52 66 44 62 Z" fill="{ROJO}"/>
  <path d="M48 46 C40 54 40 66 46 72 C44 62 48 54 56 50 Z" fill="#169C5F"/>
  <circle cx="63" cy="36" r="12" fill="{VERDE_CLARO}"/>
  <path d="M56 26 C60 16 70 18 72 24 C68 22 62 24 56 26 Z" fill="#7FE0B0"/>
  <path d="M74 36 L84 39 L74 42 Z" fill="{DORADO}"/>
  <circle cx="66" cy="34" r="3.6" fill="#ffffff"/>
  <circle cx="67" cy="34" r="1.8" fill="#0d1b14"/>
</svg>
"""


def pagina(cuerpo, ancho, alto, fondo="transparent"):
    return f"""<!doctype html><html><head><meta charset="utf-8">{FUENTES}
<style>
  html, body {{ margin:0; padding:0; width:{ancho}px; height:{alto}px; background:{fondo}; overflow:hidden; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:'Nunito', 'Inter', sans-serif; }}
</style></head><body>{cuerpo}</body></html>"""


def luminancia(color):
    color = color.lstrip("#")
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ajustar(color, factor):
    """Aclara (factor > 1) u oscurece (factor < 1) un color hexadecimal."""
    color = color.lstrip("#")
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def fotografiar(navegador, contenido, destino, ancho, alto, transparente=False):
    destino.parent.mkdir(parents=True, exist_ok=True)
    hoja = navegador.new_page(viewport={"width": ancho, "height": alto})
    hoja.set_content(contenido, wait_until="networkidle")
    hoja.evaluate("document.fonts.ready")
    tipo = "jpeg" if destino.suffix == ".jpg" else "png"
    opciones = {"path": str(destino), "type": tipo, "full_page": False}
    if tipo == "jpeg":
        opciones["quality"] = 88
    else:
        opciones["omit_background"] = transparente
    hoja.screenshot(**opciones)
    hoja.close()
    print("  ", destino.relative_to(RAIZ))


# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------
def logo_horizontal():
    return pagina(f"""
<div style="display:flex;align-items:center;gap:26px;height:320px;padding:0 30px;">
  <div style="width:250px;height:250px;">{QUETZAL_SVG}</div>
  <div>
    <div style="font-family:'Fredoka';font-weight:700;font-size:150px;line-height:1;letter-spacing:-2px;">
      <span style="color:{VERDE};">Quetzal</span><span style="color:{ROJO};">Mart</span>
    </div>
    <div style="font-family:'Nunito';font-weight:800;font-size:34px;color:{VERDE_OSCURO};letter-spacing:9px;margin-top:6px;">
      LO DE TODOS LOS DÍAS, MÁS CERCA
    </div>
  </div>
</div>""", 1280, 320)


def logo_claro():
    """Versión para fondos oscuros (encabezados de correo y pie de página)."""
    return pagina(f"""
<div style="display:flex;align-items:center;gap:22px;height:200px;padding:0 20px;">
  <div style="width:160px;height:160px;">{QUETZAL_SVG}</div>
  <div style="font-family:'Fredoka';font-weight:700;font-size:104px;line-height:1;letter-spacing:-1px;">
    <span style="color:#ffffff;">Quetzal</span><span style="color:{DORADO};">Mart</span>
  </div>
</div>""", 820, 200)


def icono(tamano):
    return pagina(f'<div style="width:{tamano}px;height:{tamano}px;">{QUETZAL_SVG}</div>',
                  tamano, tamano)


# ---------------------------------------------------------------------------
# Portadas
# ---------------------------------------------------------------------------
def fondo_diagonal():
    return (f"background: radial-gradient(circle at 85% 20%, {ajustar(VERDE_CLARO, 1.25)} 0, transparent 38%),"
            f"radial-gradient(circle at 10% 110%, {DORADO}55 0, transparent 40%),"
            f"linear-gradient(120deg, {VERDE_OSCURO} 0%, {VERDE} 55%, #0E8A5F 100%);")


def producto_por_sku(sku):
    prefijo, numero = sku.split("-")
    for datos in catalogo.CATEGORIAS_VENTA.values():
        if datos["prefijo"] == prefijo:
            nombre, presentacion, *_resto, envase, color = datos["productos"][int(numero) - 1]
            return nombre, presentacion, envase, color
    raise KeyError(sku)


def miniatura(sku, escala, giro=0):
    """Empaque reducido dentro de una caja de tamaño fijo (600 px escalados)."""
    nombre, presentacion, envase, color = producto_por_sku(sku)
    lado = int(600 * escala)
    return (f'<div style="width:{lado}px;height:{lado}px;position:relative;">'
            f'<div style="width:600px;height:600px;transform:scale({escala}) rotate({giro}deg);'
            f'transform-origin:0 0;display:flex;align-items:center;justify-content:center;">'
            f'{empaque(nombre, presentacion, envase, color)}</div></div>')


VITRINA = ["DES-009", "DES-004", "LAC-001", "SNK-004", "BEB-005", "DES-008", "CUI-004", "SNK-010"]


def mini_productos(cantidad, escala):
    giros = (-5, 3, -2, 6, 4, -6, 2, -3)
    return "".join(miniatura(sku, escala, giros[i]) for i, sku in enumerate(VITRINA[:cantidad]))


def portada_inicio():
    return pagina(f"""
<div style="position:relative;width:1920px;height:760px;{fondo_diagonal()}overflow:hidden;">
  <div style="position:absolute;left:150px;top:150px;width:820px;color:white;">
    <div style="display:inline-block;background:{DORADO};color:{VERDE_OSCURO};font-weight:800;
                padding:10px 22px;border-radius:30px;font-size:26px;letter-spacing:2px;">
      AHORA TAMBIÉN EN LÍNEA
    </div>
    <div style="font-family:'Fredoka';font-weight:700;font-size:96px;line-height:1.02;margin-top:28px;">
      Lo de todos los días,<br><span style="color:{DORADO};">más cerca de ti</span>
    </div>
    <div style="font-size:34px;margin-top:26px;opacity:.92;line-height:1.35;">
      Despensa, lácteos, bebidas, limpieza y cuidado personal a precios justos.
      Entregamos en Guatemala, México y El Salvador.
    </div>
  </div>
  <div style="position:absolute;right:60px;top:110px;width:880px;height:540px;display:flex;
              flex-wrap:wrap;align-content:center;justify-content:center;gap:4px 0;">
    {mini_productos(8, 0.36)}
  </div>
</div>""", 1920, 760)


def portada_campana():
    return pagina(f"""
<div style="position:relative;width:1200px;height:560px;{fondo_diagonal()}overflow:hidden;">
  <div style="position:absolute;left:70px;top:80px;width:600px;color:white;">
    <div style="font-family:'Fredoka';font-weight:700;font-size:44px;color:{DORADO};">Temporada QuetzalMart</div>
    <div style="font-family:'Fredoka';font-weight:700;font-size:92px;line-height:1;margin-top:12px;">
      10% <span style="font-size:56px;">de descuento</span>
    </div>
    <div style="font-size:30px;margin-top:20px;line-height:1.35;">en tu próxima compra en línea con el código</div>
    <div style="display:inline-block;margin-top:22px;background:white;color:{ROJO};font-family:'Fredoka';
                font-weight:700;font-size:54px;letter-spacing:6px;padding:10px 30px;border-radius:18px;
                border:4px dashed {ROJO};">QUETZAL10</div>
  </div>
  <div style="position:absolute;right:20px;top:40px;width:520px;height:480px;display:flex;flex-wrap:wrap;
              align-content:center;justify-content:center;">{mini_productos(6, 0.28)}</div>
</div>""", 1200, 560)


# ---------------------------------------------------------------------------
# Empaques de producto (marca propia QuetzalMart)
# ---------------------------------------------------------------------------
def etiqueta(nombre, presentacion, ancho, color):
    texto = "#13261c" if luminancia(color) > 0.55 else "#ffffff"
    franja = VERDE if luminancia(color) > 0.55 else "rgba(255,255,255,.18)"
    return f"""
<div style="width:{ancho}px;background:rgba(255,255,255,.92);border-radius:18px;padding:16px 16px 14px;
            text-align:center;box-shadow:0 4px 12px rgba(0,0,0,.12);">
  <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
    <div style="width:34px;height:34px;">{QUETZAL_SVG}</div>
    <div style="font-family:'Fredoka';font-weight:700;font-size:24px;">
      <span style="color:{VERDE};">Quetzal</span><span style="color:{ROJO};">Mart</span></div>
  </div>
  <div style="font-family:'Nunito';font-weight:800;font-size:{30 if len(nombre) < 24 else 25}px;line-height:1.12;
              color:#13261c;margin-top:10px;">{html.escape(nombre)}</div>
  <div style="display:inline-block;margin-top:10px;background:{color};color:{texto};font-weight:800;
              font-size:22px;padding:4px 16px;border-radius:14px;border:2px solid {franja};">{html.escape(presentacion)}</div>
</div>"""


def empaque(nombre, presentacion, envase, color, escala=1.0):
    oscuro = ajustar(color, 0.78)
    claro = ajustar(color, 1.18)
    brillo = ("linear-gradient(90deg, rgba(0,0,0,.18) 0%, rgba(255,255,255,.28) 22%, "
              "rgba(255,255,255,0) 45%, rgba(0,0,0,.12) 100%)")
    if envase == "bolsa":
        forma = f"""
<div style="width:380px;height:500px;position:relative;">
  <div style="position:absolute;top:0;left:0;right:0;height:46px;border-radius:10px 10px 0 0;
       background:repeating-linear-gradient(90deg,{oscuro} 0 12px,{color} 12px 24px);"></div>
  <div style="position:absolute;top:40px;left:0;right:0;bottom:0;border-radius:24px 24px 46px 46px;
       background:{brillo},{color};display:flex;align-items:center;justify-content:center;">
    {etiqueta(nombre, presentacion, 300, color)}</div></div>"""
    elif envase == "botella":
        forma = f"""
<div style="width:300px;height:560px;position:relative;display:flex;flex-direction:column;align-items:center;">
  <div style="width:96px;height:58px;border-radius:12px;background:{VERDE_OSCURO};"></div>
  <div style="width:110px;height:70px;background:linear-gradient(90deg,{oscuro},{claro},{oscuro});
       clip-path:polygon(10% 0,90% 0,100% 100%,0 100%);"></div>
  <div style="width:300px;flex:1;border-radius:70px 70px 44px 44px;background:{brillo},{color};
       display:flex;align-items:center;justify-content:center;">{etiqueta(nombre, presentacion, 250, color)}</div></div>"""
    elif envase == "lata":
        forma = f"""
<div style="width:320px;height:430px;position:relative;">
  <div style="position:absolute;inset:18px 0;background:{brillo},{color};"></div>
  <div style="position:absolute;top:0;left:0;right:0;height:40px;border-radius:50%;
       background:linear-gradient(180deg,#e6e6e6,#9da3a6);"></div>
  <div style="position:absolute;bottom:0;left:0;right:0;height:40px;border-radius:50%;background:{oscuro};"></div>
  <div style="position:absolute;inset:60px 18px;display:flex;align-items:center;justify-content:center;">
    {etiqueta(nombre, presentacion, 280, color)}</div></div>"""
    elif envase == "carton":
        forma = f"""
<div style="width:300px;height:560px;position:relative;">
  <div style="position:absolute;top:0;left:0;right:0;height:120px;background:{oscuro};
       clip-path:polygon(0 100%,18% 22%,82% 22%,100% 100%);"></div>
  <div style="position:absolute;top:0;left:30%;width:40%;height:30px;background:{oscuro};"></div>
  <div style="position:absolute;top:118px;left:0;right:0;bottom:0;border-radius:6px;background:{brillo},{color};
       display:flex;align-items:center;justify-content:center;">{etiqueta(nombre, presentacion, 260, color)}</div></div>"""
    elif envase == "frasco":
        forma = f"""
<div style="width:360px;height:470px;position:relative;display:flex;flex-direction:column;align-items:center;">
  <div style="width:300px;height:70px;border-radius:16px;background:repeating-linear-gradient(90deg,{VERDE} 0 10px,{VERDE_OSCURO} 10px 14px);"></div>
  <div style="width:360px;flex:1;border-radius:46px;margin-top:-6px;background:{brillo},{color};
       display:flex;align-items:center;justify-content:center;">{etiqueta(nombre, presentacion, 300, color)}</div></div>"""
    elif envase == "tubo":
        forma = f"""
<div style="width:300px;height:580px;position:relative;display:flex;flex-direction:column;align-items:center;">
  <div style="width:300px;height:30px;background:repeating-linear-gradient(90deg,{oscuro} 0 8px,{claro} 8px 16px);"></div>
  <div style="width:300px;height:470px;background:{brillo},{color};
       clip-path:polygon(0 0,100% 0,82% 100%,18% 100%);display:flex;align-items:flex-start;
       justify-content:center;padding-top:60px;">{etiqueta(nombre, presentacion, 220, color)}</div>
  <div style="width:120px;height:70px;border-radius:0 0 18px 18px;background:{VERDE_OSCURO};"></div></div>"""
    elif envase == "paquete":
        forma = f"""
<div style="width:560px;height:360px;position:relative;">
  <div style="position:absolute;top:0;bottom:0;left:0;width:34px;
       background:repeating-linear-gradient(180deg,{oscuro} 0 12px,{color} 12px 24px);"></div>
  <div style="position:absolute;top:0;bottom:0;right:0;width:34px;
       background:repeating-linear-gradient(180deg,{oscuro} 0 12px,{color} 12px 24px);"></div>
  <div style="position:absolute;top:0;bottom:0;left:30px;right:30px;border-radius:16px;
       background:linear-gradient(180deg,rgba(255,255,255,.3),rgba(0,0,0,.1)),{color};
       display:flex;align-items:center;justify-content:center;">{etiqueta(nombre, presentacion, 380, color)}</div></div>"""
    else:  # caja
        forma = f"""
<div style="width:420px;height:500px;position:relative;">
  <div style="position:absolute;top:0;left:30px;width:360px;height:44px;background:{claro};
       transform:skewX(-35deg);transform-origin:bottom left;"></div>
  <div style="position:absolute;top:44px;left:0;width:360px;bottom:0;background:{color};border-radius:4px;
       display:flex;align-items:center;justify-content:center;">{etiqueta(nombre, presentacion, 300, color)}</div>
  <div style="position:absolute;top:13px;left:360px;width:60px;bottom:-31px;background:{oscuro};
       transform:skewY(-35deg);transform-origin:top left;height:487px;"></div></div>"""
    return f'<div style="transform:scale({escala});transform-origin:center;">{forma}</div>'


def imagen_producto(nombre, presentacion, envase, color, tinte):
    return pagina(f"""
<div style="width:800px;height:800px;display:flex;align-items:center;justify-content:center;position:relative;
            background:radial-gradient(circle at 50% 38%, #ffffff 0, {tinte} 75%);">
  <div style="position:absolute;bottom:92px;width:440px;height:46px;border-radius:50%;
              background:radial-gradient(ellipse, rgba(0,0,0,.28), transparent 70%);"></div>
  <div style="position:relative;top:-10px;">{empaque(nombre, presentacion, envase, color)}</div>
</div>""", 800, 800)


TINTES = {
    "despensa": "#F6EEDC", "lacteos": "#E6F1FA", "bebidas": "#E3F4F1",
    "snacks": "#FBEBDD", "limpieza": "#EAF0FB", "cuidado": "#F6EAF4",
}


def imagen_categoria(clave, datos):
    productos = datos["productos"][:3]
    piezas = "".join(
        f'<div style="transform:scale(.62) rotate({giro}deg);margin:0 -70px;">'
        f'{empaque(nombre, presentacion, envase, color)}</div>'
        for (nombre, presentacion, *_r, envase, color), giro in zip(productos, (-8, 0, 8)))
    return pagina(f"""
<div style="width:800px;height:600px;position:relative;overflow:hidden;
            background:radial-gradient(circle at 50% 30%, #ffffff 0, {TINTES[clave]} 70%);">
  <div style="position:absolute;top:20px;left:0;right:0;display:flex;justify-content:center;align-items:center;height:470px;">
    {piezas}</div>
  <div style="position:absolute;left:0;right:0;bottom:0;height:120px;background:{VERDE};color:white;
              display:flex;flex-direction:column;justify-content:center;padding-left:40px;">
    <div style="font-family:'Fredoka';font-weight:700;font-size:48px;">{html.escape(datos['nombre'])}</div>
    <div style="font-size:22px;opacity:.9;">{html.escape(datos['descripcion'])}</div>
  </div>
</div>""", 800, 600)


def main():
    partes = set(sys.argv[1:]) or {"logo", "portadas", "categorias", "productos"}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        if "logo" in partes:
            print("Logo")
            fotografiar(navegador, logo_horizontal(), ADDON_IMPL / "img" / "logo_quetzalmart.png",
                        1280, 320, transparente=True)
            fotografiar(navegador, icono(512), ADDON_IMPL / "img" / "icono_quetzalmart.png",
                        512, 512, transparente=True)
            fotografiar(navegador, logo_claro(), ADDON_CRM / "img" / "logo_claro.png",
                        820, 200, transparente=True)
            for addon in ("qm_implementacion", "qm_crm_postventa", "qm_ga4_ecommerce",
                          "qm_gestion_documental", "qm_puente_rpa"):
                fotografiar(navegador, icono(256),
                            RAIZ / "odoo_addons" / addon / "static" / "description" / "icon.png",
                            256, 256, transparente=True)
        if "portadas" in partes:
            print("Portadas")
            fotografiar(navegador, portada_inicio(), ADDON_IMPL / "img" / "portada_inicio.jpg", 1920, 760)
            fotografiar(navegador, portada_campana(), ADDON_CRM / "img" / "campana_hero.png", 1200, 560)
        if "categorias" in partes:
            print("Categorías")
            for clave, datos in catalogo.CATEGORIAS_VENTA.items():
                fotografiar(navegador, imagen_categoria(clave, datos),
                            ADDON_IMPL / "img" / "categorias" / f"{clave}.png", 800, 600)
        if "productos" in partes:
            print("Productos")
            for clave, datos in catalogo.CATEGORIAS_VENTA.items():
                for numero, (nombre, presentacion, *_r, envase, color) in enumerate(datos["productos"], 1):
                    sku = f"{datos['prefijo']}-{numero:03d}"
                    fotografiar(navegador, imagen_producto(nombre, presentacion, envase, color, TINTES[clave]),
                                SALIDA_PRODUCTOS / f"{sku}.png", 800, 800)
        navegador.close()


if __name__ == "__main__":
    main()
