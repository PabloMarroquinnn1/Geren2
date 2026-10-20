# Google Analytics 4 en la tienda de QuetzalMart

## Qué ya está hecho en Odoo

| Evento GA4 | Cuándo se envía | Quién lo envía |
|---|---|---|
| `page_view` | Cada página | Odoo (etiqueta de Google) |
| `view_item` | Al abrir la ficha de un producto (una vez por página) | Odoo + `qm_ga4_ecommerce` (quita duplicados) |
| `add_to_cart` | Al pulsar *Agregar al carrito* | Odoo |
| `view_cart` | Al abrir el carrito | `qm_ga4_ecommerce` |
| `remove_from_cart` | Al eliminar un producto del carrito | `qm_ga4_ecommerce` |
| `begin_checkout` | Al pulsar *Finalizar compra* (o al entrar al pago) | `qm_ga4_ecommerce` |
| `add_shipping_info` | Al llegar al pago con el envío elegido | `qm_ga4_ecommerce` |
| `add_payment_info` | Al pulsar *Pagar ahora* | `qm_ga4_ecommerce` |
| `purchase` | En la confirmación del pedido (con número de pedido, total, IVA, envío y productos) | Odoo + `qm_ga4_ecommerce` (usa el SKU como `item_id`) |

Además se envía la propiedad de usuario `cliente_registrado` (`si`/`no`) para segmentar.
Todos los eventos de producto llevan `item_id` = SKU (`DES-009`), `item_name`, `item_category`,
`item_brand`, precio y cantidad, en quetzales (`GTQ`).

## 1. Crear la propiedad de GA4 (15 min)

1. Entrar a <https://analytics.google.com> con la cuenta del grupo (no personal).
2. **Administrar ► Crear ► Cuenta**: `QuetzalMart SOG2`. **Propiedad**: `Tienda QuetzalMart`,
   zona horaria *Guatemala*, moneda **Quetzal guatemalteco (GTQ)**. Sector: *Compras*.
3. **Flujo de datos ► Web**: URL de la tienda (`https://quetzalmart.<ip>.sslip.io`), nombre
   `Tienda en línea`. Dejar activada la **medición mejorada**.
4. Copiar el **ID de medición** (`G-XXXXXXXXXX`).
5. **Administrar ► Configuración de datos ► Retención de datos**: cambiar a **14 meses**
   (con 2 meses las exploraciones pierden la historia).

## 2. Conectar Odoo

Cualquiera de las dos formas:

* Odoo ► **Sitio web ► Configuración ► Ajustes ► Google Analytics**: activar y pegar el ID.
* O con el cargador: `python carga_masiva/cargar_quetzalmart.py --url ... --clave ... --paso configurar --ga4 G-XXXXXXXXXX`

Comprobar: abrir la tienda en otra pestaña y ver en GA4 **Informes ► Tiempo real** que aparece un
usuario. Para ver cada evento con sus parámetros: instalar la extensión *Google Analytics Debugger*
en Chrome y abrir **Administrar ► DebugView**.

## 3. Definiciones personalizadas y eventos clave

1. **Administrar ► Definiciones personalizadas ► Crear dimensión personalizada**:
   * `Cliente registrado` — ámbito **Usuario** — propiedad `cliente_registrado`.
   * `Método de envío` — ámbito **Evento** — parámetro `shipping_tier`.
   * `Forma de pago` — ámbito **Evento** — parámetro `payment_type`.
2. **Administrar ► Eventos clave**: `purchase` ya viene marcado. Marcar también `begin_checkout`
   y `add_to_cart` (sirven para la tasa de conversión de cada paso).

## 4. Generar datos

GA4 necesita interacción para mostrar informes. Además de navegar a mano (en computadora y
teléfono, desde los enlaces del correo de campaña), use el simulador:

```bash
pip install playwright && playwright install chromium
python analytics/simular_trafico.py --url https://SU-DOMINIO --visitas 40 --correo-base grupo.quetzalmart@gmail.com
```

Cada visita es un usuario nuevo que llega por Facebook, Instagram, Google (cpc), correo o directo
(`utm_source`/`utm_medium`/`utm_campaign`) y explora, abandona el carrito, abandona el pago o compra.
Hágalo **al menos 2 días antes** de la calificación: los informes estándar tardan 24-48 h; *Tiempo
real* y *DebugView* muestran los datos al instante.

## 5. Dónde se ve cada indicador que pide el enunciado

| Indicador | Dónde |
|---|---|
| **Tasa de conversión** | Informes ► Interacción ► Eventos clave (tasa de eventos clave de la sesión). En la exploración de embudo: % que llega de `view_item` a `purchase`. |
| **Adquisición de usuarios** | Informes ► Adquisición ► Adquisición de usuarios (primer grupo de canales, fuente/medio) y Adquisición de tráfico (campañas `temporada_quetzalmart`, etc.). |
| **Total de ingresos** | Informes ► Monetización ► Descripción general (Ingresos totales, Ingresos por compras). |
| **Productos más vendidos** | Informes ► Monetización ► Compras de comercio electrónico (ordenar por *Artículos comprados*). |
| **Abandono de carrito** | Exploración de embudo (paso `add_to_cart` → `purchase`: tasa de abandono) e Informes ► Monetización ► Recorrido de compra. |

## 6. Segmentos (3 de usuarios y 5 de eventos)

Los segmentos se crean dentro de una exploración: **Explorar ► Exploración de formato libre ►
Segmentos (+)**. Nombre exacto sugerido y condición:

**Segmentos de usuarios**

1. `Usuarios compradores` — Incluir usuarios cuando: evento `purchase`.
2. `Abandonaron el carrito` — Incluir: evento `add_to_cart`; **Excluir** usuarios cuando: evento `purchase`.
3. `Llegaron por correo` — Incluir usuarios cuando: *Medio del primer usuario* = `email`
   (alternativa: `Cliente registrado` = `si`).

**Segmentos de eventos**

1. `Evento - vista de producto` — evento `view_item`.
2. `Evento - agregar al carrito` — evento `add_to_cart`.
3. `Evento - inicio de pago` — evento `begin_checkout`.
4. `Evento - compra` — evento `purchase`.
5. `Evento - eliminar del carrito` — evento `remove_from_cart` (alternativas: `view_cart`, `add_payment_info`).

## 7. Exploraciones (2 informes con los segmentos)

1. **Embudo de compra QuetzalMart** (Exploración de embudo): pasos `view_item` ► `add_to_cart` ►
   `begin_checkout` ► `add_shipping_info` ► `purchase`; marcar *Embudo abierto*; comparar segmentos
   `Usuarios compradores` y `Abandonaron el carrito`; desglose por *Primer grupo de canales*.
   Muestra en qué paso se pierde la gente (abandono de carrito y de pago).
2. **Productos por segmento** (Formato libre): filas *Nombre del artículo*, columnas *Segmento*,
   valores *Artículos vistos*, *Artículos añadidos al carrito*, *Artículos comprados*, *Ingresos
   del artículo*; segmentos de eventos `Evento - vista de producto`, `Evento - agregar al carrito`
   y `Evento - compra`. Muestra qué productos se ven mucho y se compran poco.

## 8. Audiencias (3, al menos 1 personalizada)

**Administrar ► Audiencias ► Nueva audiencia ► Crear una audiencia personalizada**:

1. `Compradores QuetzalMart` — Incluir: evento `purchase`. Duración: 540 días.
2. `Carrito abandonado (7 días)` — Incluir: evento `add_to_cart`; Excluir temporalmente: evento
   `purchase`. Duración: 7 días. (Audiencia para remarketing con el código QUETZAL10.)
3. `Interesados por campañas de correo` — Incluir: *Medio de la sesión* = `email` y evento
   `view_item`. Duración: 30 días.

Las audiencias solo acumulan usuarios desde que se crean: créelas **antes** de generar el tráfico.

## 9. Para el Manual 3

Exporte cada informe con el botón **Compartir este informe ► Descargar archivo (PDF/CSV)** y anote
las cifras en `manuales/manual_3/datos_ga4.json`; `python manuales/construir_manuales.py 3` genera
las gráficas y el PDF del Manual 3 con esos datos.
