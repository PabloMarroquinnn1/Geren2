"""Genera los tres manuales en PDF a partir de los .md de esta carpeta.

    pip install markdown matplotlib playwright && playwright install chromium
    npm install --prefix manuales mermaid@11.4.1     # solo si cambia algún diagrama .mmd
    python manuales/construir_manuales.py            # los tres
    python manuales/construir_manuales.py 3          # solo el Manual 3

* Portada con los datos de datos_grupo.json.
* Diagramas: diagramas/*.mmd -> .svg y .png (requiere mermaid en node_modules; si no
  está, se usan los .svg ya generados).
* Manual 3: gráficas y cifras desde manual_3/datos_ga4.json. Mientras ese archivo tenga
  "ejemplo": true, el PDF sale marcado como BORRADOR.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
LOGO = RAIZ / "odoo_addons" / "qm_implementacion" / "static" / "img" / "logo_quetzalmart.png"
MERMAID = AQUI / "node_modules" / "mermaid" / "dist" / "mermaid.min.js"
DIAGRAMAS = AQUI / "diagramas"

MANUALES = {
    1: ("manual_1.md", "Manual 1", "Instalación, funcionamiento de los módulos, carga de información y RPA"),
    2: ("manual_2.md", "Manual 2", "Diagramas de flujo de los procesos de QuetzalMart"),
    3: ("manual_3/manual_3.md", "Manual 3", "Inteligencia de negocios con Google Analytics 4"),
}

CONFIG_MERMAID = {
    "startOnLoad": False,
    "theme": "base",
    "fontFamily": "Inter, Arial, sans-serif",
    "flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 34, "htmlLabels": True,
                  "useMaxWidth": True},
    "themeVariables": {
        "primaryColor": "#EAF4EE", "primaryBorderColor": "#0B6E4F", "primaryTextColor": "#13261c",
        "lineColor": "#064635", "clusterBkg": "#FFFBF0", "clusterBorder": "#E2C877",
        "tertiaryColor": "#FFF8E7", "fontSize": "14px",
    },
}

ESTILO = """
@page { size: Letter; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: Inter, Arial, sans-serif; color: #1d2a23; font-size: 10.5pt; line-height: 1.5; }
h1 { color: #064635; font-size: 20pt; border-bottom: 3px solid #0B6E4F; padding-bottom: 4px;
     margin-top: 0; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { color: #0B6E4F; font-size: 14pt; margin-top: 18pt; }
h3 { color: #064635; font-size: 11.5pt; margin-top: 12pt; }
h2, h3 { break-after: avoid; page-break-after: avoid; }
li { break-inside: avoid; }
.captura { break-inside: avoid; page-break-inside: avoid; }
a { color: #0B6E4F; }
code { background: #F3F7F4; padding: 1px 4px; border-radius: 4px; font-size: 9pt; }
pre { background: #0f1f18; color: #e6f2ec; padding: 10px 12px; border-radius: 8px; font-size: 8.5pt;
      white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.3pt; page-break-inside: avoid; }
th { background: #0B6E4F; color: white; text-align: left; padding: 5px 7px; }
td { border-bottom: 1px solid #dfe8e2; padding: 4px 7px; vertical-align: top; }
tr:nth-child(even) td { background: #F7FAF8; }
img { max-width: 100%; border: 1px solid #d5dfd9; border-radius: 6px; margin: 6pt 0 2pt 0; }
p > img:only-child { display: block; margin-left: auto; margin-right: auto; }
.pie { font-size: 8.5pt; color: #5b6b62; text-align: center; margin-top: 0; }
blockquote { border-left: 4px solid #C8102E; background: #FFF4F5; margin: 8pt 0; padding: 6px 12px; }
.pendiente { border: 2px dashed #C8102E; background: #FFF4F5; color: #8a1020; padding: 14px; border-radius: 8px;
             text-align: center; margin: 8pt 0; font-weight: 600; }
.diagrama { page-break-inside: avoid; text-align: center; margin: 6pt 0; }
.diagrama svg { max-width: 100%; height: auto; max-height: 205mm; }
.portada { height: 228mm; display: flex; flex-direction: column; justify-content: space-between;
           page-break-after: always; }
.portada .franja { background: linear-gradient(120deg, #064635, #0B6E4F 60%, #0E8A5F); color: white;
                   border-radius: 14px; padding: 26px 30px; }
.portada .franja h1 { color: white; border: none; font-size: 30pt; margin: 6px 0; page-break-before: avoid; }
.portada .franja .sub { font-size: 14pt; color: #F2B705; font-weight: 700; }
.portada table td { border: none; background: none !important; padding: 2px 6px; }
.toc { page-break-after: always; }
.toc ul { list-style: none; padding-left: 12px; }
.toc > ul { padding-left: 0; }
.toc a { text-decoration: none; color: #1d2a23; }
.borrador { position: fixed; top: 40%; left: 0; right: 0; text-align: center; transform: rotate(-30deg);
            font-size: 56pt; color: rgba(200, 16, 46, .12); font-weight: 800; z-index: -1; }
"""


def datos_grupo():
    ruta = AQUI / "datos_grupo.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def portada(numero, titulo, subtitulo, grupo):
    filas = "".join(f"<tr><td>{p['carne']}</td><td>{p['nombre']}</td></tr>" for p in grupo["integrantes"])
    # "grupo" y "auxiliar" son opcionales: si no están en el JSON no se muestran.
    nombre_grupo = f"<p><b>{grupo['grupo']}</b></p>" if grupo.get("grupo") else ""
    auxiliar = f"Auxiliar: {grupo['auxiliar']}<br>" if grupo.get("auxiliar") else ""
    fecha = grupo.get("fecha") or date.today().strftime("%d/%m/%Y")
    return f"""
<section class="portada">
  <div><img src="{LOGO.as_uri()}" style="width:300px;border:none"></div>
  <div class="franja">
    <div class="sub">{titulo}</div>
    <h1>{subtitulo}</h1>
    <div>Implementación ERP, comercio electrónico, gestión documental, RPA y marketing digital</div>
  </div>
  <div>
    <p><b>Universidad de San Carlos de Guatemala</b> · Facultad de Ingeniería · Ingeniería en Ciencias y Sistemas<br>
    Sistemas Organizacionales y Gerenciales 2 · Proyecto único · Segundo semestre 2026</p>
    {nombre_grupo}
    <table><tr><th>Carné</th><th>Nombre</th></tr>{filas}</table>
    <p>{auxiliar}Fecha: {fecha}</p>
  </div>
</section>"""


def renderizar_diagramas(navegador):
    if not MERMAID.exists():
        print("  (mermaid no instalado: se usan los SVG existentes)")
        return
    pagina = navegador.new_page(viewport={"width": 1400, "height": 1000}, device_scale_factor=2)
    pagina.set_content("<html><body style='background:white'><div id='d'></div></body></html>")
    pagina.add_script_tag(path=str(MERMAID))
    pagina.evaluate("cfg => mermaid.initialize(cfg)", CONFIG_MERMAID)
    for fuente in sorted(DIAGRAMAS.glob("*.mmd")):
        svg = pagina.evaluate(
            "async ([id, codigo]) => (await mermaid.render(id, codigo)).svg",
            ["diagrama" + fuente.stem.replace("_", ""), fuente.read_text(encoding="utf-8")])
        fuente.with_suffix(".svg").write_text(svg, encoding="utf-8")
        pagina.evaluate("svg => { document.getElementById('d').innerHTML = svg; }", svg)
        pagina.locator("#d svg").screenshot(path=str(fuente.with_suffix(".png")))
        print("  diagrama", fuente.stem)
    pagina.close()


def incrustar_diagramas(html):
    """![texto](diagramas/x.svg) -> SVG en línea (las etiquetas HTML de Mermaid lo requieren)."""
    def reemplazo(coincidencia):
        ruta = AQUI / coincidencia.group(2)
        if not ruta.exists():
            return f'<div class="pendiente">Falta el diagrama {coincidencia.group(2)}</div>'
        return f'<div class="diagrama">{ruta.read_text(encoding="utf-8")}</div>'
    return re.sub(r'<img alt="([^"]*)" src="(diagramas/[^"]+\.svg)"\s*/?>', reemplazo, html)


def preparar_manual_3():
    import graficos_manual_3
    datos = json.loads((AQUI / "manual_3" / "datos_ga4.json").read_text(encoding="utf-8"))
    graficos_manual_3.generar(datos, AQUI / "manual_3" / "graficos")
    return datos


def rellenar(texto, datos, prefijo=""):
    """Sustituye {{clave}} y {{grupo.clave}} por los valores del JSON."""
    for clave, valor in datos.items():
        nombre = f"{prefijo}{clave}"
        if isinstance(valor, dict):
            texto = rellenar(texto, valor, nombre + ".")
        elif not isinstance(valor, list):
            texto = texto.replace("{{" + nombre + "}}", f"{valor:,}" if isinstance(valor, int) else str(valor))
    return texto


def construir(navegador, numero, grupo):
    archivo, titulo, subtitulo = MANUALES[numero]
    fuente = AQUI / archivo
    texto = fuente.read_text(encoding="utf-8")
    borrador = False
    if numero == 3:
        datos = preparar_manual_3()
        texto = rellenar(texto, datos)
        borrador = datos.get("ejemplo", True)
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "attr_list", "toc", "sane_lists"],
                               extension_configs={"toc": {"toc_depth": "1-2"}})
    cuerpo = cuerpo.replace('<div class="toc">', '<div class="toc"><h2>Contenido</h2>', 1)
    cuerpo = incrustar_diagramas(cuerpo)
    marca = '<div class="borrador">BORRADOR · DATOS DE EJEMPLO</div>' if borrador else ""
    pagina_html = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{titulo}</title>"
                   f"<style>{ESTILO}</style></head><body>{marca}{portada(numero, titulo, subtitulo, grupo)}"
                   f"{cuerpo}</body></html>")
    temporal = fuente.parent / f"_construccion_{numero}.html"
    temporal.write_text(pagina_html, encoding="utf-8")
    pagina = navegador.new_page()
    pagina.goto(temporal.as_uri(), wait_until="networkidle")
    nombre_pdf = AQUI / f"QuetzalMart - {titulo} - {subtitulo.split(',')[0]}.pdf"
    pagina.pdf(path=str(nombre_pdf), format="Letter", print_background=True, display_header_footer=True,
               margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
               header_template=f"<div style='font-size:7px;color:#7a8a80;width:100%;text-align:right;"
                               f"padding-right:14mm'>QuetzalMart · {titulo}</div>",
               footer_template="<div style='font-size:7px;color:#7a8a80;width:100%;text-align:center'>"
                               "Página <span class='pageNumber'></span> de <span class='totalPages'></span></div>")
    pagina.close()
    temporal.unlink()
    print(f"  {nombre_pdf.name}{'  (BORRADOR)' if borrador else ''}")


def main():
    numeros = [int(n) for n in sys.argv[1:]] or [1, 2, 3]
    sys.path.insert(0, str(AQUI))
    grupo = datos_grupo()
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        if 2 in numeros:
            renderizar_diagramas(navegador)
        for numero in numeros:
            construir(navegador, numero, grupo)
        navegador.close()


if __name__ == "__main__":
    main()
