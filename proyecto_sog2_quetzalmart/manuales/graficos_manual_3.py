"""Gráficas, indicadores calculados y tablas del Manual 3 a partir de datos_ga4.json."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

VERDE = "#0B6E4F"
VERDE_OSCURO = "#064635"
ROJO = "#C8102E"
DORADO = "#F2B705"
GRIS = "#5B6B62"
PALETA = [VERDE, ROJO, DORADO, "#2E86C1", "#8E44AD", "#16A085"]


def quetzales(valor):
    return f"Q {valor:,.2f}"


def _estilo(ejes, titulo):
    ejes.set_title(titulo, loc="left", fontsize=12, fontweight="bold", color=VERDE_OSCURO, pad=12)
    for lado in ("top", "right"):
        ejes.spines[lado].set_visible(False)
    ejes.spines["left"].set_color("#c9d6ce")
    ejes.spines["bottom"].set_color("#c9d6ce")
    ejes.tick_params(colors=GRIS, labelsize=9)


def _guardar(figura, carpeta, nombre):
    figura.tight_layout()
    figura.savefig(carpeta / f"{nombre}.png", dpi=170)
    plt.close(figura)


def _barras_horizontales(carpeta, nombre, titulo, etiquetas, valores, color, formato="{:,.0f}"):
    figura, ejes = plt.subplots(figsize=(8, 0.55 * len(etiquetas) + 1.2))
    posiciones = range(len(etiquetas))[::-1]
    barras = ejes.barh(list(posiciones), valores, color=color, height=0.6)
    ejes.set_yticks(list(posiciones), etiquetas)
    for barra, valor in zip(barras, valores):
        ejes.text(barra.get_width(), barra.get_y() + barra.get_height() / 2, "  " + formato.format(valor),
                  va="center", fontsize=9, color=VERDE_OSCURO)
    ejes.set_xlim(0, max(valores) * 1.22 if valores else 1)
    _estilo(ejes, titulo)
    _guardar(figura, carpeta, nombre)


def generar(datos, carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = ["Inter", "DejaVu Sans"]

    canales = datos["adquisicion"]
    _barras_horizontales(carpeta, "01_sesiones_por_canal", "Sesiones por canal de adquisición",
                         [c["canal"] for c in canales], [c["sesiones"] for c in canales], VERDE)
    _barras_horizontales(carpeta, "02_eventos_por_sesion", "Eventos por sesión según el canal",
                         [c["canal"] for c in canales], [c["eventos_por_sesion"] for c in canales], DORADO,
                         "{:,.2f}")

    # Embudo de compra: barras proporcionales y, a la derecha, usuarios y % del paso anterior.
    pasos = datos["embudo"]
    figura, ejes = plt.subplots(figsize=(8, 0.62 * len(pasos) + 1.1))
    maximo = pasos[0]["usuarios"] or 1
    for i, paso in enumerate(pasos):
        fila = len(pasos) - i
        ancho = paso["usuarios"] / maximo
        ejes.barh(fila, ancho, color=PALETA[i % len(PALETA)], height=0.62)
        texto = f"{paso['usuarios']:,}"
        if i:
            texto += f"  ·  {paso['usuarios'] / (pasos[i - 1]['usuarios'] or 1):.0%} del paso anterior"
        ejes.text(ancho + 0.01, fila, texto, va="center", fontsize=9, color=VERDE_OSCURO)
    ejes.set_yticks([len(pasos) - i for i in range(len(pasos))], [p["paso"] for p in pasos])
    ejes.set_xlim(0, 1.55)
    ejes.set_xticks([])
    _estilo(ejes, "Embudo de compra (usuarios, segmento Usuarios compradores)")
    ejes.spines["bottom"].set_visible(False)
    _guardar(figura, carpeta, "03_embudo")

    productos = sorted(datos["productos"], key=lambda p: (p["ingresos"], p["comprados"]), reverse=True)
    _barras_horizontales(carpeta, "04_ingresos_por_producto", "Ingresos por producto (GTQ)",
                         [p["producto"] for p in productos], [p["ingresos"] for p in productos], ROJO, "Q {:,.2f}")

    figura, ejes = plt.subplots(figsize=(8, 3.6))
    nombres = [" ".join(p["producto"].split(" ")[:2]) for p in productos]
    x = range(len(productos))
    ejes.bar([i - 0.27 for i in x], [p["vistos"] for p in productos], width=0.27, label="Vistos", color="#9fc9b4")
    ejes.bar(list(x), [p["agregados"] for p in productos], width=0.27, label="Al carrito", color=DORADO)
    ejes.bar([i + 0.27 for i in x], [p["comprados"] for p in productos], width=0.27, label="Comprados", color=VERDE)
    ejes.set_xticks(list(x), nombres, rotation=25, ha="right")
    ejes.legend(frameon=False, fontsize=9)
    _estilo(ejes, "Vistos, agregados al carrito y comprados por producto")
    _guardar(figura, carpeta, "05_productos_embudo")

    paginas = datos["paginas"]
    _barras_horizontales(carpeta, "06_paginas_mas_vistas", "Páginas más vistas",
                         [p["pagina"] for p in paginas], [p["vistas"] for p in paginas], VERDE_OSCURO)
    paises = datos["paises"]
    _barras_horizontales(carpeta, "07_usuarios_por_pais", "Usuarios activos por país",
                         [p["pais"] for p in paises], [p["usuarios"] for p in paises], "#2E86C1")

    _calcular(datos, canales, pasos, productos)


def _tabla(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    lineas += ["| " + " | ".join(str(celda) for celda in fila) + " |" for fila in filas]
    return "\n".join(lineas)


def _pct(valor):
    return f"{valor:.1%}".replace(".", ",")


def _calcular(datos, canales, pasos, productos):
    resumen = datos["resumen"]
    caidas = [(pasos[i]["paso"], pasos[i + 1]["paso"],
               1 - pasos[i + 1]["usuarios"] / (pasos[i]["usuarios"] or 1)) for i in range(len(pasos) - 1)]
    peor = max(caidas, key=lambda c: c[2])
    carrito = next(p for p in pasos if "add_to_cart" in p["paso"])
    canal_sesiones = max(canales, key=lambda c: c["sesiones"])
    canal_eventos = max(canales, key=lambda c: c["eventos_por_sesion"])
    canal_debil = min(canales, key=lambda c: c["tasa_interaccion"])
    sin_venta = [p["producto"] for p in productos if p["agregados"] and not p["comprados"]]
    datos["calculado"] = {
        "ingresos": quetzales(resumen["ingresos"]),
        "ingreso_por_comprador": quetzales(resumen["ingresos"] / (resumen["compradores"] or 1)),
        "conversion_usuarios": _pct(resumen["compradores"] / (resumen["usuarios"] or 1)),
        "tasa_interaccion": _pct(resumen["sesiones_interaccion"] / (resumen["sesiones"] or 1)),
        "abandono_carrito": _pct(1 - pasos[-1]["usuarios"] / (carrito["usuarios"] or 1)),
        "peor_paso": f"{peor[0]} → {peor[1]}",
        "peor_paso_pct": _pct(peor[2]),
        "canal_sesiones": canal_sesiones["canal"],
        "canal_sesiones_n": canal_sesiones["sesiones"],
        "canal_eventos": canal_eventos["canal"],
        "canal_resumen": (f"**{canal_sesiones['canal']}** es el canal que más sesiones trae ({canal_sesiones['sesiones']}) "
                          + ("y también el de más interacción por sesión" if canal_eventos is canal_sesiones
                             else f"y **{canal_eventos['canal']}** el de más interacción por sesión")),
        "canal_debil": canal_debil["canal"],
        "canal_debil_pct": f"{canal_debil['tasa_interaccion']} %",
        "producto_top": productos[0]["producto"],
        "producto_top_ingresos": quetzales(productos[0]["ingresos"]),
        "producto_unidades": max(productos, key=lambda p: p["comprados"])["producto"],
        "productos_sin_venta": " y ".join(sin_venta) if sin_venta else "ninguno",
    }
    datos["tablas"] = {
        "adquisicion": _tabla(["Canal", "Sesiones", "Con interacción", "Tasa de interacción", "Eventos por sesión",
                               "Tiempo medio"],
                              [[c["canal"], c["sesiones"], c["sesiones_interaccion"], f"{c['tasa_interaccion']} %",
                                f"{c['eventos_por_sesion']:.2f}".replace(".", ","), c["tiempo_medio"]] for c in canales]),
        "paginas": _tabla(["Página", "Vistas"], [[p["pagina"], p["vistas"]] for p in datos["paginas"]]),
        "embudo": _tabla(["Paso", "Usuarios", "% del paso anterior", "% del inicio"],
                         [[p["paso"], p["usuarios"],
                           "—" if i == 0 else f"{p['usuarios'] / (pasos[i - 1]['usuarios'] or 1):.0%}",
                           f"{p['usuarios'] / (pasos[0]['usuarios'] or 1):.0%}"] for i, p in enumerate(pasos)]),
        "productos": _tabla(["Producto", "Vistos", "Al carrito", "Comprados", "Ingresos"],
                            [[p["producto"], p["vistos"], p["agregados"], p["comprados"], quetzales(p["ingresos"])]
                             for p in productos]),
        "segmentos_usuarios": _tabla(["Segmento de usuarios", "Condición"],
                                     [[s["nombre"], s["condicion"]] for s in datos["segmentos_usuarios"]]),
        "segmentos_eventos": _tabla(["Segmento de eventos", "Evento"],
                                    [[s["nombre"], f"`{s['evento']}`"] for s in datos["segmentos_eventos"]]),
        "exploraciones": _tabla(["Exploración", "Técnica", "Segmentos", "Hallazgo"],
                                [[e["nombre"], e["tecnica"], e["segmentos"], e["hallazgo"]] for e in datos["exploraciones"]]),
        "audiencias": _tabla(["Audiencia", "Condición", "Usuarios"],
                             [[a["nombre"], a["condicion"], a["usuarios"]] for a in datos["audiencias"]]),
    }
