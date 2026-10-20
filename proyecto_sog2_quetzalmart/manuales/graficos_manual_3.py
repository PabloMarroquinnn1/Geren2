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
    _barras_horizontales(carpeta, "01_usuarios_por_canal", "Usuarios por canal de adquisición",
                         [c["canal"] for c in canales], [c["usuarios"] for c in canales], VERDE)
    _barras_horizontales(carpeta, "02_ingresos_por_canal", "Ingresos por canal (GTQ)",
                         [c["canal"] for c in canales], [c["ingresos"] for c in canales], DORADO, "Q {:,.2f}")

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
    _estilo(ejes, "Embudo de compra (usuarios)")
    ejes.spines["bottom"].set_visible(False)
    _guardar(figura, carpeta, "03_embudo")

    productos = sorted(datos["productos"], key=lambda p: p["comprados"], reverse=True)
    _barras_horizontales(carpeta, "04_productos_mas_vendidos", "Productos más vendidos (unidades compradas)",
                         [p["producto"] for p in productos], [p["comprados"] for p in productos], ROJO)

    figura, ejes = plt.subplots(figsize=(8, 3.6))
    nombres = [p["producto"].split(" ")[0] + " " + p["producto"].split(" ")[1] for p in productos]
    x = range(len(productos))
    ejes.bar([i - 0.27 for i in x], [p["vistos"] for p in productos], width=0.27, label="Vistos", color="#9fc9b4")
    ejes.bar(list(x), [p["agregados"] for p in productos], width=0.27, label="Al carrito", color=DORADO)
    ejes.bar([i + 0.27 for i in x], [p["comprados"] for p in productos], width=0.27, label="Comprados", color=VERDE)
    ejes.set_xticks(list(x), nombres, rotation=25, ha="right")
    ejes.legend(frameon=False, fontsize=9)
    _estilo(ejes, "Vistos, agregados al carrito y comprados por producto")
    _guardar(figura, carpeta, "05_productos_embudo")

    campanas = datos["campanas"]
    _barras_horizontales(carpeta, "06_ingresos_por_campana", "Ingresos por campaña (fuente / medio)",
                         [c["fuente_medio"] for c in campanas], [c["ingresos"] for c in campanas], VERDE_OSCURO,
                         "Q {:,.2f}")

    dispositivos = datos["dispositivos"]
    figura, ejes = plt.subplots(figsize=(5, 3.4))
    ejes.pie([d["usuarios"] for d in dispositivos], labels=[d["dispositivo"] for d in dispositivos],
             colors=PALETA, autopct="%1.0f%%", startangle=90, wedgeprops={"width": 0.42},
             textprops={"fontsize": 9, "color": VERDE_OSCURO})
    ejes.set_title("Usuarios por dispositivo", loc="left", fontsize=12, fontweight="bold", color=VERDE_OSCURO)
    _guardar(figura, carpeta, "07_dispositivos")

    _calcular(datos, canales, pasos, productos, campanas, dispositivos)


def _tabla(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    lineas += ["| " + " | ".join(str(celda) for celda in fila) + " |" for fila in filas]
    return "\n".join(lineas)


def _calcular(datos, canales, pasos, productos, campanas, dispositivos):
    resumen = datos["resumen"]
    carrito = next((p for p in pasos if "add_to_cart" in p["paso"]), pasos[1])
    compra = pasos[-1]
    caidas = [(pasos[i]["paso"], pasos[i + 1]["paso"],
               1 - pasos[i + 1]["usuarios"] / (pasos[i]["usuarios"] or 1)) for i in range(len(pasos) - 1)]
    peor = max(caidas, key=lambda c: c[2])
    canal_ingresos = max(canales, key=lambda c: c["ingresos"])
    canal_usuarios = max(canales, key=lambda c: c["usuarios"])
    canal_conversion = max(canales, key=lambda c: c["compras"] / (c["sesiones"] or 1))
    mas_visto_poco_comprado = max(productos, key=lambda p: p["vistos"] - 4 * p["comprados"])
    dispositivo = max(dispositivos, key=lambda d: d["usuarios"])
    total_disp = sum(d["usuarios"] for d in dispositivos) or 1
    datos["calculado"] = {
        "ingresos": quetzales(resumen["ingresos"]),
        "ticket_promedio": quetzales(resumen["ingresos"] / (resumen["compras"] or 1)),
        "abandono_carrito": f"{1 - compra['usuarios'] / (carrito['usuarios'] or 1):.0%}",
        "conversion_carrito": f"{compra['usuarios'] / (carrito['usuarios'] or 1):.0%}",
        "peor_paso": f"{peor[0]} → {peor[1]}",
        "peor_paso_pct": f"{peor[2]:.0%}",
        "canal_ingresos": canal_ingresos["canal"],
        "canal_ingresos_monto": quetzales(canal_ingresos["ingresos"]),
        "canal_usuarios": canal_usuarios["canal"],
        "canal_conversion": canal_conversion["canal"],
        "canal_conversion_pct": f"{canal_conversion['compras'] / (canal_conversion['sesiones'] or 1):.1%}",
        "producto_top": productos[0]["producto"],
        "producto_top_unidades": productos[0]["comprados"],
        "producto_oportunidad": mas_visto_poco_comprado["producto"],
        "dispositivo_top": dispositivo["dispositivo"],
        "dispositivo_top_pct": f"{dispositivo['usuarios'] / total_disp:.0%}",
    }
    datos["tablas"] = {
        "adquisicion": _tabla(["Canal", "Usuarios", "Sesiones", "Compras", "Ingresos", "Conversión"],
                              [[c["canal"], c["usuarios"], c["sesiones"], c["compras"], quetzales(c["ingresos"]),
                                f"{c['compras'] / (c['sesiones'] or 1):.1%}"] for c in canales]),
        "campanas": _tabla(["Campaña", "Fuente / medio", "Sesiones", "Compras", "Ingresos"],
                           [[c["campana"], c["fuente_medio"], c["sesiones"], c["compras"], quetzales(c["ingresos"])]
                            for c in campanas]),
        "embudo": _tabla(["Paso", "Usuarios", "% del paso anterior", "% del inicio"],
                         [[p["paso"], p["usuarios"],
                           "—" if i == 0 else f"{p['usuarios'] / (pasos[i - 1]['usuarios'] or 1):.0%}",
                           f"{p['usuarios'] / (pasos[0]['usuarios'] or 1):.0%}"] for i, p in enumerate(pasos)]),
        "productos": _tabla(["Producto", "Vistos", "Al carrito", "Comprados", "Ingresos", "Compra / vista"],
                            [[p["producto"], p["vistos"], p["agregados"], p["comprados"], quetzales(p["ingresos"]),
                              f"{p['comprados'] / (p['vistos'] or 1):.0%}"] for p in productos]),
        "segmentos_usuarios": _tabla(["Segmento de usuarios", "Condición", "Usuarios"],
                                     [[s["nombre"], s["condicion"], s["usuarios"]] for s in datos["segmentos_usuarios"]]),
        "segmentos_eventos": _tabla(["Segmento de eventos", "Evento", "Eventos"],
                                    [[s["nombre"], f"`{s['evento']}`", s["eventos"]] for s in datos["segmentos_eventos"]]),
        "exploraciones": _tabla(["Exploración", "Técnica", "Segmentos", "Hallazgo"],
                                [[e["nombre"], e["tecnica"], e["segmentos"], e["hallazgo"]] for e in datos["exploraciones"]]),
        "audiencias": _tabla(["Audiencia", "Condición", "Usuarios"],
                             [[a["nombre"], a["condicion"], a["usuarios"]] for a in datos["audiencias"]]),
    }
