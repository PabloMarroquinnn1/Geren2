# Bloque 7 — Google Analytics 4

## Resultado

El bloque de analítica quedó implementado sobre la tienda web de QuetzalMart y configurado en la propiedad GA4:

- Cuenta: `QuetzalMart GEREN2 2026`
- Propiedad: `QuetzalMart Web 2026`
- ID de medición: `G-ZB34R27HPD`
- Portal: `https://quetzalmart.34-9-149-41.sslip.io`

La instalación del seguimiento se realiza mediante la vista QWeb `qm_ga4_tracking`, definida por `infra/seed_block7_ga4.py`. La vista carga `gtag.js` y registra los eventos de comercio electrónico directamente desde el portal, sin utilizar una API de Odoo desde UiPath.

## Eventos implementados

| Evento | Momento de disparo |
|---|---|
| `view_item` | Visualización de una ficha de producto |
| `add_to_cart` | Adición de un producto al carrito |
| `begin_checkout` | Entrada al proceso de checkout |
| `purchase` | Visualización de la confirmación de pedido |

Todos los eventos incluyen moneda `GTQ`; los eventos de producto incluyen nombre, identificador, precio y cantidad. El evento `purchase` incluye identificador de transacción y valor total cuando la página de confirmación los presenta.

## Segmentos de usuarios guardados

Se guardaron en la propiedad GA4 los tres segmentos solicitados:

1. `Usuarios con visualizacion de producto` — evento `(view_item)`.
2. `Usuarios con carrito` — evento `(add_to_cart)`.
3. `Usuarios compradores` — evento `(purchase)`.

## Segmentos de eventos guardados

Se guardaron cinco segmentos de evento en la propiedad:

1. `Evento view_item` — `(view_item)`.
2. `Evento add_to_cart` — `(add_to_cart)`.
3. `Evento begin_checkout` — `(begin_checkout)`.
4. `Evento purchase` — `(purchase)`.
5. `Evento abandono_carrito` — `(add_to_cart)`.

El quinto segmento deja identificada la actividad de carrito para el análisis de abandono. El abandono se interpreta comparando usuarios que añadieron al carrito contra quienes posteriormente completan `purchase`; GA4 no requiere crear un evento ficticio adicional para este caso.

## Exploraciones guardadas

- `Exploracion 1 - Segmentos de usuarios` — exploración de formato libre para comparar los segmentos de usuarios.
- `Exploracion 2 - Segmentos de eventos` — exploración de formato libre para comparar los segmentos de eventos.

La interfaz de GA4 limita la visualización simultánea de comparaciones en una exploración, pero los cinco segmentos de eventos quedan guardados a nivel de propiedad y pueden seleccionarse para completar la comparación requerida.

## Audiencias publicadas

Además de las audiencias automáticas `All Users` y `Purchasers`, se publicaron estas tres audiencias personalizadas:

1. `Audiencia visitantes de producto` — incluye usuarios con `(view_item)`.
2. `Audiencia añadieron al carrito` — incluye usuarios con `(add_to_cart)`.
3. `Audiencia compradores` — incluye usuarios con `(purchase)`.

Con esto se cumplen las tres audiencias obligatorias y se incluyen audiencias personalizadas, sin contar la audiencia automática de abandono de carrito.

## Validación y consideración para la evaluación

La fuente pública fue verificada para confirmar la presencia de `G-ZB34R27HPD`, `view_item`, `add_to_cart`, `begin_checkout` y `purchase`. Los objetos de GA4 quedaron guardados el 20 de septiembre de 2026.

GA4 puede tardar en mostrar datos de eventos en los informes estándar y las audiencias inicialmente aparecen con menos de 10 usuarios. Antes de la evaluación conviene navegar nuevamente por un producto, agregarlo al carrito, entrar al checkout y completar una compra de prueba; después se deben revisar los informes de eventos, monetización y adquisición.

