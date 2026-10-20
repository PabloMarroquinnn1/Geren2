[TOC]

# Introducción

Este manual describe con diagramas de flujo los procesos de QuetzalMart tal como quedaron
implementados en Odoo 18, la tienda en línea, el gestor documental y el robot de UiPath. Cada
diagrama usa **carriles** (recuadros) para indicar quién realiza cada actividad.

| Símbolo | Significado |
|---|---|
| Óvalo | Inicio o fin del proceso |
| Rectángulo | Actividad o registro en el sistema |
| Rombo | Decisión |
| Paralelogramo | Dato que ingresa una persona |
| Recuadro con título | Carril: área o sistema responsable |

Las tres sucursales (Guatemala, México y El Salvador) siguen el mismo proceso; cada una tiene su
almacén con seis sectores: **Abarrotes secos**, **Cámara de refrigeración**, **Químicos y
limpieza**, **Bazar y cuidado personal**, **Materiales operativos** y **Cuarentena (producto no
conforme)**.

# 1. Robot de UiPath: carga de clientes y productos

## 1a. Recorrido de carpetas, elección de hoja y consolidación

![Recorrido del robot](diagramas/01a_rpa_recorrido.svg)

## 1b. Importación en Odoo por la interfaz web

![Importación en Odoo](diagramas/01b_rpa_importacion.svg)

## Descripción

El auxiliar entrega una carpeta con subcarpetas cuyos nombres empiezan con
*clientes*, *proveedores*, *reclamos*, *registro* o *productos*, seguidos de un guion y una
descripción. El robot:

1. Pide la carpeta raíz y busca todos los `.xlsx` en todas las subcarpetas.
2. Lee los nombres de las hojas de cada libro en el orden de las pestañas.
3. Toma la hoja de la **5.ª posición** si se llama *clientes* o *productos*; si el libro no la
   tiene en esa posición, la busca por nombre (sin distinguir mayúsculas, tildes ni espacios).
4. Reconoce las columnas aunque vengan en inglés o en español, normaliza los valores y descarta
   filas vacías y registros repetidos.
5. Junta todo en dos consolidados y los carga en Odoo con **Importar registros** (Subir archivo ►
   Probar ► Importar). Si Odoo encuentra un error en la prueba, el robot se detiene sin importar.
6. Guarda `reporte_robot.xlsx` con cada archivo, hoja, posición y cantidad de registros.

La información queda visible en Odoo (Contactos y Productos, filtro *Cargados por el RPA*), en la
tienda en línea (productos publicados) y en la base de datos (consultas SQL, sección 9).

# 2. Compras a proveedores

## 2a. Necesidad, cotización y orden de compra

![Solicitud y orden de compra](diagramas/02a_compras_solicitud.svg)

## 2b. Recepción, factura del proveedor y pago

![Recepción y pago](diagramas/02b_compras_recepcion_pago.svg)

## Descripción detallada

* **Detección de la necesidad.** El encargado de bodega revisa en *Inventario ► Reabastecimiento*
  los productos y materiales por debajo del mínimo de su sucursal.
* **Cotización.** Compras crea una **solicitud de cotización (SDC)** a dos o tres proveedores del
  rubro y la envía desde Odoo. Se comparan precio, calidad, tiempo de entrega y crédito.
* **Orden de compra.** La SDC elegida se confirma y se convierte en **orden de compra**. Las
  compras mayores a **Q 10,000** pasan por la aprobación de un gerente (configurado en Odoo).
* **Recepción.** La sucursal recibe contra la orden: cuenta unidades, revisa fechas de
  vencimiento, empaques y, en lácteos, la temperatura. Lo no conforme se separa en
  **Cuarentena** y se gestiona devolución o nota de crédito. Al validar la recepción, Odoo ubica
  cada producto en el sector que le corresponde (reglas de ubicación por categoría).
* **Factura y pago.** Contabilidad crea la factura del proveedor desde la orden, concilia orden,
  recepción y factura (tres vías), la publica, archiva el PDF FEL en *Documentos ► Facturas de
  proveedores* y programa el pago según el crédito.

| Documento en Odoo | Ejemplo | Dónde verlo |
|---|---|---|
| Solicitud de cotización | `P00001` (`SDC-001`) | Compras ► Solicitudes de cotización |
| Orden de compra | `P00021` (`OC-001`) | Compras ► Órdenes de compra |
| Recepción | `GUA/IN/00001` | Inventario ► Recepciones |
| Factura de proveedor | `FACTU/2026/08/0001` (`FEL-PRV-…`) | Contabilidad ► Facturas de proveedores |

# 3. Ventas de productos

## 3a. Canales, cotización y pedido

![Cotización y pedido](diagramas/03a_ventas_cotizacion.svg)

## 3b. Despacho, facturación y cobro

![Despacho y cobro](diagramas/03b_ventas_despacho_cobro.svg)

## Descripción detallada

* **Canales.** Los clientes compran en la **tienda física** (caja), en la **tienda en línea**
  (diagrama 5) o, si son empresas, mediante **cotización** (hoteles, comedores, colegios).
* **Cotización.** Ventas registra al cliente en *Contactos*, abre una **oportunidad** en el CRM,
  prepara la cotización (`COT-…`) con productos, cantidades, precios e IVA del 12 % y la envía.
* **Pedido.** Cuando el cliente acepta, la cotización se confirma como **pedido de venta**, Odoo
  reserva el inventario de la sucursal y la oportunidad queda **ganada**.
* **Despacho.** La bodega toma los productos del sector correspondiente, los empaca, etiqueta y
  valida la entrega (el inventario baja). Si no hay existencias se genera una compra urgente.
* **Facturación y cobro.** Se crea y publica la factura (PDF archivado automáticamente en
  *Documentos ► Facturas de venta*) y se registra el pago de contado o se da seguimiento al cobro.

# 4. Flujo del producto: de la recepción a la venta

## 4a. Recepción y productos defectuosos o en mal estado

![Recepción y defectuosos](diagramas/04a_producto_recepcion.svg)

## 4b. Almacenamiento por sector y control de inventario

![Almacenamiento y control](diagramas/04b_producto_almacen_control.svg)

## 4c. Empaque y control de calidad para la venta

![Empaque y calidad](diagramas/04c_producto_empaque_calidad.svg)

## Descripción por etapa

1. **Recepción del producto.** Se verifica contra la orden de compra (producto, cantidad, lote y
   vencimiento). Los productos de cadena de frío se reciben solo si llegan a 4 °C o menos.
2. **Almacenamiento según su sector.** Odoo aplica reglas de ubicación por categoría: despensa,
   bebidas y snacks a **Abarrotes secos**; lácteos a **Cámara de refrigeración**; limpieza a
   **Químicos y limpieza**, separado de los alimentos; cuidado personal a **Bazar y cuidado
   personal**; insumos internos a **Materiales operativos**.
3. **Productos defectuosos o en mal estado.** Todo producto no conforme (en la recepción, en un
   conteo o en el control final) pasa a **Cuarentena**. Si la causa es del proveedor se devuelve
   y se pide nota de crédito; si es interna o está vencido se registra como **merma** (desecho).
   Queda constancia en el gestor documental.
4. **Control de inventario.** Rotación PEPS (primero en vencer, primero en salir), conteos
   cíclicos semanales con *Inventario físico*, ajustes con motivo y reabastecimiento cuando un
   producto baja del mínimo.
5. **Empaque.** Se fracciona, empaca y etiqueta con precio (IVA incluido). Los pedidos en línea se
   arman con etiqueta de envío.
6. **Control de calidad para ponerlo a la venta.** Se revisa empaque, etiqueta, precio,
   vencimiento y código de barras. Lo aprobado se exhibe en góndola y se publica en la tienda en
   línea; lo rechazado regresa a Cuarentena.

# 5. Recorrido del cliente: compra en línea y visita a la tienda

## 5a. Compra en línea: del anuncio al carrito

![Navegación y carrito](diagramas/05a_cliente_web_carrito.svg)

## 5b. Compra en línea: pago y lo que hace Odoo después

![Pago y postventa](diagramas/05b_cliente_web_pago.svg)

## 5c. Visita a la tienda física

![Tienda física](diagramas/05c_cliente_tienda_fisica.svg)

## Descripción detallada

* **Compra en línea.** El cliente llega desde un anuncio o desde el correo de campaña (los enlaces
  llevan parámetros UTM que GA4 registra). Explora el catálogo, agrega productos al carrito, ve el
  subtotal, el IVA y el costo de envío, puede aplicar el código **QUETZAL10** y finaliza la compra
  como invitado o creando una cuenta (lo que lo registra como **lead** en el CRM). Elige entrega a
  domicilio o recoger en sucursal y paga con tarjeta.
* **Después del pago.** Odoo confirma el pedido, crea y publica la factura, marca la oportunidad
  como ganada, archiva el PDF y envía **dos correos**: el comprobante de compra y, después, la
  campaña de marketing con su descuento.
* **Visita a la tienda.** El cliente recorre los pasillos por sector, pide ayuda si la necesita y
  paga en caja; si trae un pedido en línea para recoger, se le entrega con su número de pedido.
  En la salida se le invita a registrarse en la tienda en línea.
* **Medición.** Cada paso de la compra en línea genera un evento de GA4 (`view_item`,
  `add_to_cart`, `view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`,
  `purchase`), que alimenta el análisis del Manual 3.
