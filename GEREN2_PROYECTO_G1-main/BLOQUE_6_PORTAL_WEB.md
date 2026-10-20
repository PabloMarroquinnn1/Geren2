# Bloque 6 — Portal web y comercio electrónico

## Resultado

Se configuró y publicó el portal de comercio electrónico de QuetzalMart en Odoo Community 18. La tienda está disponible por HTTPS en:

`https://quetzalmart.34-9-149-41.sslip.io`

La implementación utiliza la misma base PostgreSQL central `quetzalmart`; no se creó una base separada para el sitio web.

## Identidad visual

- Logotipo original de QuetzalMart con fondo transparente.
- Portada propia con el mensaje «Todo lo que necesitas, más cerca de ti».
- Imágenes originales para Abarrotes, Bebidas, Limpieza, Hogar, Cuidado personal y Tecnología.
- Fotografías de producto separadas de las imágenes de categoría: 60 imágenes específicas, una por SKU, generadas según el nombre real de cada producto.
- Página de inicio, navegación, contacto y pie de página adaptados al español.
- Datos públicos de contacto configurados como `info@quetzalmart.local` y `+502 2200 2026`.

Los recursos se encuentran en `assets/brand/`. Se generaron específicamente para este proyecto mediante el generador de imágenes integrado; el conjunto de instrucciones visuales cubrió una portada de supermercado regional sin texto, seis bodegones para las categorías, 60 fotografías de producto y un logotipo transparente.

## Catálogo

| Elemento | Resultado |
|---|---:|
| Productos publicados | 60 |
| Productos con imagen | 60 |
| Categorías públicas | 6 |
| Productos por página | 24 |
| Moneda | GTQ |
| Idioma predeterminado | Español latinoamericano (`es_419`) |

Cada producto tiene referencia `QM-*`, precio, descripción comercial, imagen, categoría e IVA de venta del 12 %.

Las imágenes de las tarjetas de categoría se mantienen como identidad visual de cada familia; las tarjetas de producto utilizan el conjunto independiente de `assets/brand/product_assets/`, con correspondencia directa `QM-001.png` a `QM-060.png`.

## Entrega y pago

- Transportista publicado: **Envío estándar QuetzalMart**.
- Tarifa fija: **Q25**, mostrada con su tratamiento tributario correspondiente.
- Envío gratuito a partir de **Q300**.
- Países admitidos: Guatemala, México y El Salvador.
- Proveedor de pago **Demo** habilitado exclusivamente en modo de prueba.
- Facturación automática habilitada después del pago confirmado.

La integración de Google Analytics 4 y la validación de sus eventos, incluido el evento de compra, corresponden al bloque 7. Si GA4 no reconoce el pago de prueba, se aplicará la alternativa indicada por el auxiliar: configurar una pasarela real.

## Prueba integral realizada

Se recorrió el proceso completo desde Brave mediante el complemento de control del navegador:

1. Apertura del catálogo público.
2. Selección de un producto y agregado al carrito.
3. Verificación de subtotal e IVA.
4. Registro de una dirección de prueba en Guatemala.
5. Selección del envío estándar.
6. Pago autorizado con el proveedor Demo.
7. Confirmación del pedido web.
8. Creación y publicación automática de la factura.

Resultado de control:

| Dato | Valor |
|---|---|
| Pedido | `S00171` |
| Estado | Confirmado (`sale`) |
| Subtotal | Q34.43 |
| Impuestos | Q4.13 |
| Total | Q38.56 |
| Transacción | Demo, procesada correctamente |
| Factura | `INV/2026/00151` |
| Estado de factura | Publicada |

## Archivos reproducibles

- `infra/install_block6_modules.sh`: instalación del módulo de entregas.
- `infra/seed_block6.py`: configuración idempotente del portal, catálogo, imágenes, envío, pago y facturación automática.
- `infra/seed_block7_product_images.py`: asignación idempotente de las fotografías de producto por categoría y SKU.
- `infra/run_block6_seed.sh`: ejecución controlada en la instancia de Odoo.
- `consultas_sql/bloque6_verificacion.sql`: consultas SQL listas para la evaluación.
- `assets/brand/`: logotipo, portada e imágenes de categorías.
- `assets/brand/product_assets/`: 60 fotografías de producto, una por SKU.

## Verificación

La comprobación final confirmó 60 productos publicados con imagen y 60 huellas visuales distintas, un único transportista web publicado, proveedor Demo en modo de prueba, idioma `es_419`, 24 productos por página y el pedido `S00171` vinculado a la factura publicada `INV/2026/00151`. La primera y segunda fila de Abarrotes se revisaron visualmente: arroz, frijol, azúcar, harina, pasta, aceite, atún y cereal muestran objetos correspondientes a sus nombres.
