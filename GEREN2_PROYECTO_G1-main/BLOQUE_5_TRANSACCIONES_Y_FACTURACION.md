# Bloque 5 — Transacciones y facturación

## Resultado

Se generó la actividad comercial mínima solicitada para QuetzalMart dentro de la base PostgreSQL central `quetzalmart`. Las cotizaciones permanecen separadas de las órdenes confirmadas para que cada requisito pueda demostrarse mediante una consulta independiente.

## Conteos finales

| Elemento | Cantidad | Estado |
|---|---:|---|
| Cotizaciones de venta | 20 | Borrador/enviada |
| Cotizaciones de compra | 20 | Borrador/enviada |
| Ventas | 150 | Confirmadas |
| Compras | 100 | Confirmadas y recibidas |
| Facturas de cliente | 150 | Publicadas |
| Facturas de proveedor | 100 | Publicadas |
| Facturas exportadas a PDF | 50 | Verificadas |

Esto aplica la aclaración del auxiliar: son 20 cotizaciones de venta y 20 de compra; las 100 compras deben estar confirmadas y tener sus facturas de proveedor validadas.

## Distribución de ventas

| Sucursal | Ventas confirmadas |
|---|---:|
| Sucursal Guatemala | 50 |
| Sucursal México | 50 |
| Sucursal El Salvador | 50 |

Cada venta contiene tres productos seleccionados de forma determinista entre las 60 referencias `QM-*`, usa diferentes cantidades y rota entre los 30 clientes disponibles.

## Flujo de compras

Cada una de las 100 compras sigue el flujo funcional de Odoo:

1. Creación de solicitud de pedido.
2. Confirmación de la orden de compra.
3. Creación y validación de la recepción en el almacén asignado.
4. Creación de la factura de proveedor vinculada a las líneas de compra.
5. Publicación de la factura en contabilidad.

Los proveedores, productos y sucursales se alternan para evitar que todas las transacciones representen el mismo caso.

## Flujo de ventas

Cada una de las 150 ventas incluye cliente, sucursal, tres productos, cantidades, precios e IVA. Las órdenes están confirmadas y tienen una factura de cliente publicada y vinculada.

Las referencias de control `B5-SALE-*`, `B5-SQ-*`, `B5-PO-*` y `B5-PQ-*` permiten comprobar el alcance del bloque sin confundirlo con las operaciones que se crearán durante la evaluación.

## Facturas PDF

Las primeras 50 facturas de cliente se exportaron mediante el reporte oficial de Odoo y se almacenaron en `outputs/facturas_pdf/`. La revisión automatizada confirmó:

- exactamente 50 archivos;
- un documento PDF válido por factura;
- una página legible por documento;
- importes, IVA, cliente, productos y referencia visibles;
- ausencia de cortes o superposiciones en la versión final.

Los rótulos del reporte se conservaron en inglés porque la traducción estándar `es_419` de Odoo 18 desbordó encabezados largos durante la inspección visual. La interfaz administrativa permanece en español. La plantilla y el logotipo se personalizarán junto con la identidad visual del portal en el bloque 6.

## Archivos reproducibles

- `infra/seed_block5.py`: creación idempotente de cotizaciones, ventas, compras, recepciones, facturas y PDF.
- `infra/run_block5_seed.sh`: ejecución controlada dentro de Odoo y comprobación de disponibilidad.
- `consultas_sql/bloque5_verificacion.sql`: consultas listas para la evaluación.
- `outputs/facturas_pdf/`: carpeta con los 50 comprobantes exigidos.

## Verificación realizada

Las consultas SQL devolvieron 20 cotizaciones de cada tipo, 150 ventas, 100 compras, 150 facturas de cliente y 100 facturas de proveedor. El sitio continuó disponible mediante HTTPS con respuesta HTTP 200 después del proceso.
