# Control de evidencias — QuetzalMart

Este archivo registra qué debe demostrarse durante la implementación y la evaluación.

| Bloque | Evidencia | Estado |
|---|---|---|
| 1 | Estructura del proyecto y plantillas de carga | Completado |
| 2 | Proyecto GCP, VM y acceso remoto | Completado |
| 3 | Odoo Community y PostgreSQL en la nube | Completado |
| 4 | Configuración de módulos, almacenes y datos base | Completado |
| 5 | Compras, ventas, cotizaciones y facturación | Completado |
| 6 | Sitio web, catálogo, carrito, impuestos y pago | Completado |
| 7 | Google Analytics 4, segmentos, audiencias y exploraciones | Completado |
| 8 | Flujo RPA en UiPath usando la interfaz de importación | En implementación |
| 9 | Consultas SQL para la evaluación | Pendiente |
| 10 | Capturas y trazabilidad de resultados | Pendiente |
| 11 | Manuales 1, 2 y 3 | Pendiente |
| 12 | Ensayo de evaluación y revisión final | Pendiente |

## Bloque 2 — Infraestructura creada

- Proyecto: `quetzalmart-geren2-2026` — **QuetzalMart GEREN2 2026**.
- API habilitada: Compute Engine.
- VM: `quetzalmart-odoo`.
- Región/zona: `us-central1-a`.
- Sistema operativo: Ubuntu 24.04 LTS.
- Tipo de máquina: `e2-standard-2` — 2 vCPU y aproximadamente 8 GB de RAM.
- Disco raíz: 30 GB `pd-balanced`.
- IP externa estática: `34.9.149.41`.
- Red: VPC `default`, con acceso web preparado en los puertos 80 y 443.
- Verificación: acceso SSH exitoso mediante Google Cloud CLI.

> La IP es un dato de infraestructura, no una contraseña. Las credenciales y claves privadas no se guardarán en este repositorio.

## Bloque 3 — Odoo Community y PostgreSQL

- Odoo Community 18 desplegado mediante la imagen oficial `odoo:18.0`.
- PostgreSQL 16 desplegado en la misma VM mediante `postgres:16-alpine`.
- Base centralizada: `quetzalmart`.
- Empresa y administrador inicial configurados como QuetzalMart.
- Acceso público: `https://quetzalmart.34-9-149-41.sslip.io`.
- Certificado TLS válido de Let's Encrypt con renovación automática.
- HTTP redirige automáticamente a HTTPS.
- PostgreSQL no está expuesto a Internet.
- Los puertos internos 8069 y 8072 de Odoo solo escuchan en `127.0.0.1` y se publican mediante Nginx.
- Credenciales almacenadas localmente en `.secrets/odoo_credentials.txt`, carpeta excluida por `.gitignore`.
- Verificación SQL: base `quetzalmart`, compañía `QuetzalMart`, administrador `admin@quetzalmart.local` y 120 tablas iniciales.

## Entregable del bloque 1

La plantilla de trabajo se encuentra en el archivo generado dentro de `outputs/`. Incluye hojas para inicio, clientes, productos, empleados, cargos y departamentos, ventas, compras y documentos.

## Bloque 4 — Configuración funcional y datos base

- 12 módulos validados: Ventas, Compras, Inventario, Facturación/Contabilidad, Empleados, Contratos, CRM, Comercio electrónico, Marketing por correo, localización de Guatemala, Documentos DMS y pago de demostración.
- La gestión documental se implementó con el módulo Community de OCA DMS, compatible con Odoo 18.
- Idioma `es_419` instalado; compañía ubicada en Guatemala y moneda principal GTQ.
- Tres almacenes en una sola compañía: Guatemala (`GT`), México (`MX`) y El Salvador (`SV`).
- Datos activos: 5 departamentos, 6 puestos, 35 empleados y 35 contratos.
- Datos comerciales: 30 clientes, 25 proveedores y 60 productos con referencia `QM-001` a `QM-060`.
- Existencias iniciales: 4,800 unidades en Guatemala, 3,300 en México y 2,700 en El Salvador.
- Catálogo web publicado con 60 productos, seis categorías y precios en quetzales; la tienda presenta 20 productos por página.
- Impuestos disponibles: IVA ventas 12 %, IVA compras 12 %, retención IVA -12 % y retención ISR -5 %.
- Repositorio documental `Documentos QuetzalMart` con estructura inicial de directorios y categorías.
- Gestión documental verificada el 29/09/2026: OCA DMS instalado; carpeta raíz visible para el administrador; tres subcarpetas (`Facturas de proveedores`, `Contratos de outsourcing`, `Contratos de empleados`) con 5 PDF cada una. Los 15 archivos tienen categoría y dos etiquetas (tipo documental y `2026`). Ruta de Odoo: `https://quetzalmart.34-9-149-41.sslip.io/odoo/action-245/1/action-245`.
- Las cinco facturas PDF se exportaron desde facturas de proveedor **contabilizadas** en Odoo (`account.move` 151-155; `BILL/2026/08/0001` a `0005`) y se vincularon a esos registros en DMS.
- Los cinco documentos de empleados son **acuerdos de demostración** hechos con los datos de `hr.contract` 1-5. Incluyen estilo editorial, cláusulas ilustrativas y registro del flujo; llevan aviso visible de que son simulados, no firmados y sin validez jurídica.
- Los cinco documentos de outsourcing son **acuerdos simulados completos** vinculados a los proveedores de Odoo (`res.partner` 72-76), con servicios, alcance, fechas, tarifas de ejemplo, responsabilidades y un ciclo demostrativo de preparación, revisión, aceptación simulada y archivo. Las partes y términos son ficticios; no constituyen contratos vigentes.
- La instalación marca el módulo Odoo `sign` como `uninstallable`; por ello el ciclo se representó en los PDF, mediante la etiqueta DMS `Flujo demo completado` y una nota interna en el historial de cada uno de los cinco documentos de outsourcing. No se enviaron solicitudes a terceros ni se registraron firmas electrónicas.
- Los acuerdos simulados usan un diseño verde y naranja, con jerarquía visual, tablas y avisos destacados. Las cinco facturas conservan el PDF oficial emitido por Odoo.
- Copias de los 15 PDF están en `outputs/dms_verified/`; se comprobó que abren y contienen texto legible, y se inspeccionó visualmente una factura, un acuerdo laboral y un acuerdo outsourcing. Las capturas de pantalla de Odoo siguen pendientes de guardarse como archivos de evidencia.
- Proveedor de pago de demostración habilitado para validar el flujo de compra antes de integrar Google Analytics 4.
- Validación reproducible disponible en `consultas_sql/bloque4_verificacion.sql`.

## Bloque 5 — Transacciones y facturación

- 20 cotizaciones de venta conservadas en borrador, adicionales a las ventas.
- 20 cotizaciones de compra conservadas en borrador, adicionales a las compras.
- 150 ventas confirmadas y facturadas: 50 para cada una de las tres sucursales.
- 100 compras confirmadas, recibidas y vinculadas a 100 facturas de proveedor publicadas.
- 150 facturas de cliente publicadas y contabilizadas.
- 50 facturas de venta exportadas físicamente a `outputs/facturas_pdf/`.
- Los 50 PDF se validaron estructuralmente y una muestra se renderizó para comprobar que no tuviera cortes, superposiciones ni contenido ilegible.
- Consultas preparadas en `consultas_sql/bloque5_verificacion.sql`.

## Bloque 7 — Google Analytics 4

- Propiedad configurada: `QuetzalMart Web 2026`, ID de medición `G-ZB34R27HPD`.
- Seguimiento instalado mediante la vista QWeb `qm_ga4_tracking`, ejecutada por `infra/seed_block7_ga4.py`.
- Eventos implementados: `view_item`, `add_to_cart`, `begin_checkout` y `purchase`.
- Tres segmentos de usuarios guardados: `Usuarios con visualizacion de producto`, `Usuarios con carrito` y `Usuarios compradores`.
- Cinco segmentos de eventos guardados: `Evento view_item`, `Evento add_to_cart`, `Evento begin_checkout`, `Evento purchase` y `Evento abandono_carrito`.
- Dos exploraciones guardadas: `Exploracion 1 - Segmentos de usuarios` y `Exploracion 2 - Segmentos de eventos`.
- Tres audiencias personalizadas publicadas: `Audiencia visitantes de producto`, `Audiencia añadieron al carrito` y `Audiencia compradores`.
- Detalle operativo, condiciones y validación: `BLOQUE_7_GOOGLE_ANALYTICS.md`.
- Nota: los eventos y audiencias recién creados pueden tardar en reflejar datos en los informes de GA4.

## Bloque 8 — RPA en UiPath

- Flujo base creado en rpa/QuetzalMart_RPA/Main.xaml.
- El robot solicita una carpeta raíz y recorre archivos .xlsx de forma recursiva.
- Detecta únicamente las hojas exactas clientes y productos.
- Lee las hojas, genera archivos temporales de una sola hoja y prepara la importación.
- La carga se realiza mediante la interfaz web de Odoo; no se utiliza API de Odoo ni inserción directa en PostgreSQL.
- Los pasos de UI dependientes de la sesión están identificados con TODO Indicar para capturar los selectores reales en UiPath Studio.
- Explicación operativa y lista de evidencias: BLOQUE_8_RPA.md.

## Bloque 6 — Portal web y comercio electrónico

- Portal público personalizado y disponible mediante HTTPS.
- Logotipo, portada, seis imágenes de categorías y 60 fotografías de producto creados específicamente para QuetzalMart.
- 60 productos publicados con imagen, descripción, precio en GTQ e IVA del 12 %.
- Las fotografías de producto están separadas de las imágenes de categoría y se asignan uno a uno por SKU, usando una imagen generada según el nombre real de cada producto.
- Seis categorías públicas y catálogo configurado para mostrar 24 productos por página.
- Envío estándar publicado con tarifa de Q25 y gratuidad desde Q300 para Guatemala, México y El Salvador.
- Proveedor Demo habilitado en modo de prueba y facturación automática activa.
- Flujo integral validado desde Brave: catálogo, carrito, dirección, entrega, pago y confirmación.
- Pedido web de control `S00171`, total Q38.56, confirmado y facturado mediante `INV/2026/00151` publicada.
- Consultas preparadas en `consultas_sql/bloque6_verificacion.sql`.
