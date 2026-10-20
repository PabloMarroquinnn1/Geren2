# Guion para el día de la calificación

Orden sugerido (unos 30 minutos). Tenga abiertos: Odoo (como administrador), la tienda en una
ventana privada, DBeaver con `sql/consultas_calificacion.sql`, UiPath Studio con el robot, GA4 y la
bandeja del correo de la empresa.

## Antes (el día anterior)

- [ ] `sudo ./respaldo.sh` en la VM.
- [ ] `python carga_masiva/cargar_quetzalmart.py --url ... --clave ... --paso verificar` (todo en OK).
- [ ] Una compra de prueba completa: llegan los dos correos (comprobante y campaña).
- [ ] UiPath: ejecución con `rpa/carpeta_prueba` sin errores; `urlOdoo` con el dominio correcto;
      Chrome con la extensión de UiPath y sesión iniciada en Odoo.
- [ ] GA4 con datos de al menos 48 horas; segmentos, exploraciones y audiencias guardados.
- [ ] Los tres manuales en PDF entregados en UEDI.

## 1. Infraestructura (2 min)

1. Consola de la nube: la VM encendida, IP estática.
2. `https://SU-DOMINIO` con candado HTTPS. En la VM: `sudo docker compose ps` (db, odoo, caddy).
3. DBeaver conectado por túnel SSH: consulta **0** (base, usuario y versión de PostgreSQL).

## 2. ERP y datos cargados (8 min)

Mostrar cada requisito en Odoo **y** con su consulta SQL:

| Requisito | En Odoo | SQL |
|---|---|---|
| 150 ventas con distintos clientes y productos | Ventas ► Órdenes | 1.1, 1.2, 1.3 |
| 20 cotizaciones a clientes y proveedores | Ventas ► Cotizaciones; Compras ► Solicitudes | 2.1, 2.2, 2.3 |
| 35 empleados, 6 cargos, 5 departamentos | Empleados (con jefe, sucursal, contrato) | 3.1, 3.2, 3.3 |
| 100 compras y sus facturas | Compras ► Pedidos; Contabilidad ► Facturas de proveedor | 4.1, 4.2 |
| 60 materiales | Inventario ► Productos (categoría *Materiales operativos*) | 5.1, 5.2 |
| 50 facturas y sus PDF en una carpeta | Documentos ► Archivo QuetzalMart ► Facturas de venta | 6.1, 6.2, 6.3 |

## 3. Tienda en línea, GA4 y marketing (8 min)

1. El auxiliar abre la tienda, **crea su cuenta** (queda como lead en CRM ► Leads, etiqueta
   *Registro web*).
2. Navega, agrega productos, ve en el carrito el **IVA y el envío**, finaliza la compra y paga con
   la tarjeta de prueba.
3. Mientras compra: GA4 ► **Tiempo real** (o DebugView) muestra `view_item`, `add_to_cart`,
   `begin_checkout`, `purchase`.
4. Llegan al correo del auxiliar: **comprobante de compra** con la factura PDF y, menos de un
   minuto después, la **campaña** con QUETZAL10 (asuntos distintos, remitente de la empresa).
5. En Odoo: el pedido, la factura publicada, la oportunidad **ganada** en el CRM y el **nuevo PDF**
   en *Documentos ► Facturas de venta* (consulta 6.3 lo muestra primero). Consultas 7.2, 10.2 y 11.
6. GA4: informes de adquisición, monetización (ingresos y productos más vendidos), la exploración
   de embudo (abandono de carrito), los segmentos y las audiencias.

## 4. Gestión documental (3 min)

*Documentos*: carpetas, filtro por **categoría** y **etiquetas** (Proveedor, Outsourcing, Recursos
humanos, Confidencial, Vigente). Abrir una factura de proveedor, un contrato de outsourcing y un
contrato laboral. Consulta 12.

## 5. RPA (8 min)

1. El auxiliar entrega su carpeta. Abrir `Main.xaml` y explicar el flujo (Manual 1, sección 4).
2. **Ejecutar**, elegir la carpeta. Mostrar el panel de salida (archivos y hojas encontradas, 5.ª
   posición) y la importación en Chrome (Subir ► Probar ► Importar).
3. Al terminar: resumen, `reporte_robot.xlsx` y los consolidados.
4. Verificar en Odoo (filtro *Cargados por el RPA* en Contactos y Productos), en la tienda
   (`/shop`, productos publicados) y en SQL (sección 9).

## Si algo falla

| Síntoma | Qué hacer |
|---|---|
| No llega un correo | Ajustes ► Técnico ► Correos (modo desarrollador): ver el error; revisar la clave de aplicación. |
| El PDF de la factura tarda | Lo genera una tarea en segundo plano en segundos; botón *Archivar PDF en Documentos* en la factura. |
| UiPath no encuentra un botón | Clic en la actividad ► *Indicar en pantalla* ► guardar y volver a ejecutar. |
| GA4 no muestra datos recientes | Usar *Tiempo real* / *DebugView*; los informes estándar tardan hasta 48 h. |
