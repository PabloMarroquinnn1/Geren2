# QuetzalMart

## Manual 1 — Instalación y operación del sistema

**Proyecto:** GEREN2 · Segundo semestre 2026  
**Versión del manual:** 1.1<br>
**Fecha:** 7 de octubre de 2026<br>
**Plataforma:** Google Cloud Platform · Ubuntu 24.04 · Docker · Odoo Community 18 · PostgreSQL 16 · UiPath

> Este documento describe el entorno y los procedimientos del proyecto académico QuetzalMart. Los clientes, proveedores, empleados, pedidos y documentos de demostración son datos simulados. No se deben copiar contraseñas, llaves ni archivos de `.secrets` a este manual.

### Contenido

1. [Instalación del sistema](#1-instalación-del-sistema)
2. [Funcionamiento de los módulos](#2-funcionamiento-de-los-módulos)
3. [Carga de información y operación en Odoo](#3-carga-de-información-y-operación-en-odoo)
4. [RPA de UiPath: flujo, evidencia y ventajas](#4-rpa-de-uipath-flujo-evidencia-y-ventajas)
5. [Comprobación de resultados](#5-comprobación-de-resultados)
6. [Anexo B: carga por módulo](#anexo-b---carga-de-información-por-módulo)
7. [Anexo C: enlaces de acceso al proyecto](#anexo-c---enlaces-de-acceso-al-proyecto)

---

# 1. Instalación del sistema

## 1.1 Arquitectura utilizada

El sistema se despliega en una máquina virtual de Google Cloud. Odoo y PostgreSQL se ejecutan como contenedores Docker en la misma VM. Nginx recibe el tráfico web y lo dirige a Odoo; el certificado HTTPS se administra con Let's Encrypt. La base de datos permanece en una red privada de Docker y no se publica en Internet.

| Componente | Configuración del proyecto |
|---|---|
| Proyecto de Google Cloud | `quetzalmart-geren2-2026` |
| VM | `quetzalmart-odoo` |
| Zona | `us-central1-a` |
| Sistema operativo | Ubuntu 24.04 LTS |
| Tipo de máquina | `e2-standard-2` (2 vCPU, 8 GB RAM) |
| Disco | 30 GB, `pd-balanced` |
| IP pública estática | `34.9.149.41` |
| Aplicación | Imagen oficial `odoo:18.0` |
| Base de datos | Imagen `postgres:16-alpine`; base `quetzalmart` |
| Proxy y HTTPS | Nginx y Let's Encrypt |
| Dirección web | [https://quetzalmart.34-9-149-41.sslip.io](https://quetzalmart.34-9-149-41.sslip.io) |

## 1.2 Requisitos previos

- Cuenta de Google Cloud con permiso para administrar el proyecto y la VM.
- Google Cloud CLI instalado en el equipo que administra la instancia.
- Acceso SSH a la VM autorizado por el proyecto.
- Este repositorio disponible localmente en el equipo administrador.
- UiPath Studio instalado en el equipo que ejecutará el robot.
- Google Chrome y la extensión de UiPath habilitada para la automatización del RPA. El flujo fue preparado para Chrome; no se deben recapturar selectores en otro navegador sin probarlos.
- Acceso a Internet para descargar imágenes de contenedor, módulos y el certificado HTTPS durante una instalación nueva.

## 1.3 Crear la VM y preparar la red

En Google Cloud Console:

1. Seleccionar el proyecto `quetzalmart-geren2-2026` y habilitar Compute Engine.
2. Crear una instancia en `us-central1-a`, con Ubuntu 24.04 LTS, `e2-standard-2` y disco de 30 GB `pd-balanced`.
3. Reservar una IP externa estática y asignarla a la VM. Para este proyecto se usa `34.9.149.41`.
4. Permitir tráfico entrante TCP por los puertos **80 y 443** para el sitio. Restringir SSH a operadores autorizados.
5. **No abrir el puerto 5432 a Internet.** PostgreSQL se mantiene dentro de la red privada de Docker. Para una comprobación administrativa puntual, usar un túnel SSH autorizado.
6. Confirmar que la IP responde y que el nombre `quetzalmart.34-9-149-41.sslip.io` resuelve a la IP reservada. El script del proyecto solicita el certificado HTTPS para ese nombre.

## 1.4 Instalar Docker, PostgreSQL, Odoo y HTTPS

Los archivos de despliegue están en `infra/`. El procedimiento siguiente describe una instalación nueva; **no volver a ejecutar el instalador en la VM que contiene la base operativa sin preparar y verificar antes un respaldo**.

Desde PowerShell, en la raíz del repositorio:

```powershell
gcloud config set project quetzalmart-geren2-2026
gcloud compute ssh quetzalmart-odoo --project=quetzalmart-geren2-2026 --zone=us-central1-a
```

Copiar los archivos de infraestructura al área temporal del servidor y ejecutar el instalador:

```powershell
gcloud compute ssh quetzalmart-odoo --project=quetzalmart-geren2-2026 --zone=us-central1-a --command="sudo mkdir -p /tmp/quetzalmart-deploy"
gcloud compute scp .\infra\docker-compose.yml .\infra\odoo.conf .\infra\nginx-quetzalmart.conf .\infra\deploy_odoo18.sh quetzalmart-odoo:/tmp/quetzalmart-deploy/ --project=quetzalmart-geren2-2026 --zone=us-central1-a
gcloud compute ssh quetzalmart-odoo --project=quetzalmart-geren2-2026 --zone=us-central1-a --command="sudo bash /tmp/quetzalmart-deploy/deploy_odoo18.sh"
```

El instalador del proyecto:

1. Instala Docker, Docker Compose, Nginx, Certbot y utilidades requeridas.
2. Copia la configuración a `/opt/quetzalmart` y configura Nginx.
3. Genera secretos aleatorios para PostgreSQL, Odoo y el administrador; los restringe a permisos de sistema.
4. Inicia PostgreSQL y espera a que esté listo.
5. En una base nueva, inicializa Odoo y la base `quetzalmart`.
6. Inicia Odoo y configura el certificado HTTPS.
7. Verifica que la página de inicio de sesión responda por HTTPS.

Los secretos generados no deben pegarse en el chat, capturas ni manual. En el servidor se almacenan fuera del repositorio, con permisos restringidos. El listado público de bases de datos de Odoo se desactiva y el filtro limita el servicio a la base `quetzalmart`.

## 1.5 Instalar las aplicaciones y los datos base

El archivo `infra/install_block4_modules.sh` instala los módulos funcionales y el complemento OCA DMS. `infra/run_block4_seed.sh` carga la configuración y los datos maestros. Para una instalación nueva, se copian esos archivos a `/tmp/quetzalmart-block4/` en la VM y se ejecutan en este orden:

1. `install_block4_modules.sh`
2. `run_block4_seed.sh`

El bloque instala Ventas, Compras, Inventario, Contabilidad, Empleados, Contratos, CRM, Comercio electrónico, Marketing por correo, localización de Guatemala, OCA DMS y el proveedor de pago de demostración.

Después, los datos comerciales se preparan mediante los scripts incluidos en `infra/`:

- `seed_block5.py` y `run_block5_seed.sh`: cotizaciones, órdenes, recepciones y facturas de venta y compra.
- `seed_block6.py` y `run_block6_seed.sh`: tienda, productos, envío, imágenes y flujo de pago.
- `seed_block7_ga4.py`: integración GA4 y eventos de comercio electrónico.

Estos scripts son parte de la implementación del proyecto. Deben ejecutarse con la base correcta y siguiendo las instrucciones de cada script; no se deben lanzar directamente sobre otra base ni durante una evaluación en curso. El robot UiPath, por separado, carga clientes y productos mediante la interfaz web de Odoo.

Para completar el archivo documental y el archivado automático de facturas:

1. Instalar OCA DMS y crear en Odoo la carpeta raíz **Documentos QuetzalMart** y sus subcarpetas/categorías.
2. Copiar el complemento `infra/odoo_addons/quetzalmart_invoice_dms/` al directorio adicional de Odoo, que se monta como `/mnt/extra-addons` dentro del contenedor.
3. Ejecutar `infra/install_invoice_dms_module.sh` para instalar o actualizar `quetzalmart_invoice_dms` en la base `quetzalmart`.
4. Importar los 50 PDFs históricos a **Documentos QuetzalMart → Facturas PDF** con `infra/archive_existing_invoices_to_dms.py`.
5. Publicar una factura de prueba y verificar que el PDF aparezca en esa carpeta. El módulo genera y archiva el PDF después de publicar una factura de cliente o proveedor.

Los 5 PDF de facturas de proveedores, 5 acuerdos simulados de outsourcing y 5 acuerdos simulados de empleados se clasifican también en DMS. Los acuerdos de empleados y proveedores son documentos académicos no firmados y no crean obligaciones legales.

## 1.6 Verificar el despliegue

1. Abrir el acceso ERP/CRM indicado en la sección 2 y comprobar la pantalla de inicio de sesión.
2. Iniciar sesión con la cuenta administrativa entregada al equipo por el medio seguro correspondiente. El manual no almacena la contraseña.
3. Abrir el menú de aplicaciones y comprobar que los módulos instalados estén disponibles.
4. Confirmar la presencia de las compañías, sucursales/almacenes, productos y contactos del proyecto.
5. Comprobar que el certificado del navegador sea válido y que HTTP redirija a HTTPS.
6. Comprobar que no exista una regla pública de firewall para PostgreSQL (5432).

**Archivos de instalación relacionados:** `infra/deploy_odoo18.sh`, `infra/docker-compose.yml`, `infra/odoo.conf`, `infra/nginx-quetzalmart.conf`, `infra/install_block4_modules.sh`, `infra/run_block4_seed.sh`.

---

# 2. Funcionamiento de los módulos

**Acceso al ERP/CRM:** [https://quetzalmart.34-9-149-41.sslip.io/odoo](https://quetzalmart.34-9-149-41.sslip.io/odoo).

| Módulo | Para qué se usa en QuetzalMart | Datos y relación con otros módulos |
|---|---|---|
| **Ventas** | Crear cotizaciones, confirmar pedidos y generar facturas de cliente. | 20 cotizaciones y 150 pedidos confirmados; las ventas se relacionan con clientes, productos, inventario y contabilidad. |
| **Compras** | Solicitar precios, confirmar órdenes y controlar recepción de mercadería. | 20 cotizaciones de compra y 100 órdenes confirmadas y recibidas; cada compra se relaciona con una factura de proveedor. |
| **Inventario** | Administrar productos, existencias, ubicaciones y ajustes físicos. | 60 productos y tres almacenes: Guatemala, México y El Salvador. Los ajustes contados se aplican con motivo y confirmación. |
| **Facturación/Contabilidad** | Publicar y consultar facturas de clientes y proveedores, impuestos y saldos. | 150 facturas de cliente y 100 de proveedor. Hay 50 PDF de facturas de cliente en `outputs/facturas_pdf/`. |
| **Contactos y CRM** | Mantener datos de clientes/proveedores y registrar oportunidades comerciales, etapas y actividades. | 30 clientes y 25 proveedores de prueba. Las órdenes del portal se asocian al ERP y se sincronizan con el trabajo comercial del CRM. |
| **Empleados y Contratos** | Administrar fichas de personal, puestos, departamentos y contratos internos. | 35 empleados, 6 puestos, 5 departamentos y 35 contratos simulados. |
| **Sitio web y eCommerce** | Publicar el catálogo, permitir carrito, calcular envío/impuestos y recibir pedidos web. | Catálogo de 60 productos en GTQ; pago Demo, únicamente para pruebas. |
| **Marketing por correo** | Crear y enviar campañas diferenciadas de las comunicaciones transaccionales. | El sistema puede generar correos de pedido/factura y campaña. La captura de Mailpit prueba recepción local, no entrega a una cuenta externa. |
| **OCA DMS (Documentos)** | Centralizar y clasificar archivos por carpetas/categorías y etiquetas. | Complemento comunitario integrado a Odoo; incluye carpetas para facturas de proveedores, contratos de outsourcing y contratos de empleados. Los contratos simulados no están firmados ni tienen validez legal. |
| **Google Analytics 4** | Medir navegación y embudo de compra en la tienda. | Eventos `view_item`, `add_to_cart`, `begin_checkout` y `purchase`; segmentos, exploraciones y audiencias se documentan en el Manual 3. Los informes estándar pueden tardar en procesarse. |
| **Pago Demo** | Ensayar el checkout sin cobrar dinero. | Es un método de prueba, no una pasarela de pago real ni una captura de fondos. |

---

# 3. Carga de información y operación en Odoo

## 3.1 Dos mecanismos de carga

El proyecto utiliza dos mecanismos distintos, según el tipo de dato:

1. **Carga inicial reproducible:** los datos maestros y las transacciones del escenario académico se generan con los scripts de `infra/`. Esto evita crear manualmente cientos de registros y permite comprobar los conteos con consultas SQL.
2. **RPA evaluable:** UiPath lee los archivos Excel del auxiliar y realiza las importaciones de clientes y productos mediante la interfaz web de Odoo. No usa API de Odoo ni escribe directamente en PostgreSQL.

Los libros del auxiliar que se probaron están en `datos/prueba_rpa/lote_auxiliar/`. El robot detecta las hojas con nombre exacto `clientes` y `productos`; se deben respetar también los encabezados del archivo, no renombrar las hojas y revisar los campos relacionales contra los valores existentes en Odoo.

## 3.2 Importar clientes o productos desde Odoo

Estos pasos son útiles para revisar una importación o hacerla manualmente:

1. Iniciar sesión en Odoo y abrir **Contactos** para clientes o **Productos** para artículos.
2. Cambiar a vista de lista si Odoo abre las tarjetas.
3. Abrir **Acciones** y seleccionar **Importar registros**.
4. Elegir **Subir archivo de datos** y seleccionar el Excel correspondiente.
5. Verificar que la hoja detectada sea exactamente `clientes` o `productos` y que la primera fila tenga los encabezados.
6. Revisar el mapeo de cada columna. Las relaciones —por ejemplo, país, categoría o etiqueta— deben coincidir con un registro existente cuando el campo lo requiera.
7. Pulsar **Probar**. Resolver todos los errores que Odoo marque antes de continuar.
8. Pulsar **Importar** y esperar el resultado. Después buscar algunos registros recién cargados y confirmar nombre, referencia y datos clave.

> Un campo vacío no siempre produce error: depende de si es obligatorio en Odoo. No se debe inventar información para llenar columnas opcionales. En cambio, el nombre del producto y los datos requeridos del cliente deben venir completos. Una cantidad física sólo aplica a un producto almacenable/seguido por inventario; no se debe asignar cantidad a un servicio.

![Interfaz auténtica de importación de productos en Odoo](../capturas/manual_1/11_importacion_productos_odoo.png)

*Figura 1. Pantalla de Odoo para subir el archivo de productos. La imagen muestra la interfaz de importación, no un resultado exitoso por sí sola; el resultado se confirma después de probar, importar y buscar el registro.*

## 3.3 Clientes y uso del CRM

Para crear o revisar un cliente:

1. Abrir **Contactos** y pulsar **Nuevo**.
2. Seleccionar si el registro es una persona o una empresa.
3. Completar nombre, correo, teléfono, país/dirección e identificación fiscal cuando corresponda.
4. Definir las etiquetas de clasificación disponibles y guardar.
5. Abrir **CRM** para revisar oportunidades, etapa, responsable y actividades asociadas. Un contacto y una oportunidad son registros relacionados, pero no son lo mismo.
6. Para validar un cliente importado, buscarlo en Contactos por nombre o correo y abrir su ficha.

![Ficha real de un contacto de prueba en Odoo](../capturas/manual_1/03_contacto_cliente_crm.png)

*Figura 2. Ficha de un contacto de demostración con datos de dirección, correo y teléfono. El nombre “RPA Cliente Prueba Completa 2026” identifica datos de prueba, no una persona o compañía real.*

![Vista real del directorio de contactos en Odoo](../capturas/manual_1/14_directorio_contactos_odoo.png)

*Figura 3. Directorio de contactos de Odoo. En esta vista pueden coexistir clientes y proveedores; se deben usar los filtros de tipo de contacto para separar ambos grupos.*

![Contactos importados por el RPA: PRUEBA SS 1 a 4](../capturas/manual_1/23_contactos_RPA_PRUEBA_SS_1_a_4.png)

*Figura 4. Resultado visible de la carga: aparecen los cuatro contactos de prueba importados por el RPA.*

## 3.4 Productos e inventario

Los 60 artículos del catálogo inicial utilizan referencias `QM-001` a `QM-060`. Para revisar un producto, abrir **Inventario → Productos** o **Ventas → Productos**, buscar por referencia y confirmar tipo de producto, unidad, precio, costo, categoría y seguimiento de existencias.

![Ficha de producto de demostración en Odoo](../capturas/manual_1/08_producto_demostracion.png)

*Figura 5. Ficha de un producto de demostración usado para probar la configuración de precio, costo y seguimiento de inventario. No debe confundirse con el conjunto maestro `QM-001` a `QM-060`.*

![Catálogo público de productos de QuetzalMart](../capturas/manual_1/02_catalogo_productos.png)

*Figura 6. Catálogo del sitio web con imágenes, nombres y precios de los productos.*

En la carga de inventario físico:

1. Abrir **Inventario → Operaciones → Ajustes de inventario**.
2. Importar/actualizar las cantidades contadas en las líneas que correspondan a productos almacenables.
3. Usar **Probar** antes de importar y corregir los errores de producto o tipo.
4. En la lista, revisar las cantidades contadas y la diferencia.
5. Si se usa **Aplicar todo**, Odoo abre el diálogo de motivo. Escribir el motivo reemplazando el texto predeterminado; no concatenarlo con `Quantity Updated`.
6. Pulsar **Actualizar cantidades** para confirmar el ajuste. Revisar después las existencias del producto/almacén.

![Lista real de ajustes de inventario](../capturas/manual_1/04_ajustes_inventario.png)

*Figura 7. Lista de ajustes de inventario y acción de aplicación.*

![Diálogo de motivo para aplicar ajustes](../capturas/manual_1/15_motivo_ajuste_inventario.png)

*Figura 8. Diálogo de Odoo que solicita el motivo del ajuste y la confirmación **Actualizar cantidades**.*

## 3.5 Órdenes de compra y recepción

Cada compra que cuenta para el requisito debe estar confirmada; una solicitud de cotización todavía no es una compra realizada.

1. Abrir **Compras → Órdenes** y localizar una solicitud o crear una nueva.
2. Seleccionar el proveedor y agregar productos, cantidades y precios.
3. Guardar y pulsar **Confirmar** para convertirla en orden de compra.
4. Abrir la recepción vinculada, revisar cantidades recibidas y pulsar **Validar**.
5. Desde la orden, pulsar **Crear factura**. Verificar proveedor, referencia y líneas.
6. Publicar la factura de proveedor. El estado publicado es el que demuestra que existe la factura contable asociada.

![Listado auténtico de solicitudes y órdenes de compra](../capturas/manual_1/05_ordenes_compra_listado.png)

*Figura 9. Vista de compras. La lista muestra 120 registros en esa captura; los indicadores superiores separan cotizaciones, órdenes y métricas de la vista.*

![Orden de compra P00120 con recepción y factura vinculadas](../capturas/manual_1/06_orden_compra_detalle.png)

*Figura 10. Orden `P00120`, asociada a un proveedor, con acceso a factura de proveedor y recepción.*

![Factura de proveedor vinculada a la orden P00120](../capturas/manual_1/07_factura_proveedor_odoo.png)

*Figura 11. Factura de proveedor `BILL/2026/08/0064`, asociada a la referencia de compra `B5-PO-100`. Para comprobarla, confirmar que el estado sea publicado/registrado.*

## 3.6 Ventas, cotizaciones y facturas de cliente

Para registrar una venta desde la interfaz:

1. Abrir **Ventas → Órdenes → Cotizaciones** y pulsar **Nuevo**.
2. Seleccionar un cliente, fecha y productos; revisar cantidad, precio e impuestos.
3. Guardar la cotización. Si el cliente acepta, pulsar **Confirmar** para obtener una orden de venta.
4. Desde la orden confirmada, elegir **Crear factura**, usar la modalidad normal y revisar las líneas.
5. Publicar la factura y, cuando se requiera evidencia documental, descargar/imprimir el PDF.

En los datos del proyecto hay **20 cotizaciones de venta** y **150 ventas confirmadas**. Las compras tienen su propio bloque de 20 cotizaciones de proveedor, separadas de las cotizaciones de venta.

![Listado de órdenes de venta de Odoo con el contador de registros](../capturas/manual_1/01_ventas_ordenes_162.png)

*Figura 12. Lista de órdenes de venta en Odoo. Se observan 162 registros en total, pedidos recientes y su estado de facturación.*

![Detalle de la venta web S00178 con pago y factura](../capturas/manual_1/16_venta_web_S00178_pago_y_factura.png)

*Figura 13. Orden de venta web `S00178`, con pago de demostración registrado y acceso a la factura asociada. El método Demo sirve para pruebas y no representa un cobro real.*

## 3.7 Empleados y contratos

Para registrar a una persona del equipo:

1. Abrir **Empleados → Empleados** y pulsar **Nuevo**.
2. Completar nombre y datos de trabajo; asignar el puesto y departamento correctos.
3. Guardar y abrir la sección de contratos del empleado.
4. Crear el contrato de demostración con fechas, puesto y condiciones académicas; guardar.
5. Volver a la lista y usar filtros/agrupación para verificar empleados por departamento y puesto.

Los datos del proyecto contemplan 35 empleados activos, seis puestos, cinco departamentos y 35 contratos simulados. Los archivos de contratos del paquete documental son **borradores simulados sin firma**; no deben presentarse como contratos legales vigentes.

![Lista de empleados de Odoo con 35 registros](../capturas/manual_1/17_empleados_35_registros.png)

*Figura 14. Vista de empleados; el paginador muestra los 35 registros del proyecto.*

![Cinco departamentos y sus cantidades de empleados](../capturas/manual_1/18_departamentos_5_registros.png)

*Figura 15. Directorio de departamentos con los conteos asociados de empleados.*

![Seis puestos de trabajo configurados](../capturas/manual_1/19_puestos_6_cargos.png)

*Figura 16. Catálogo de puestos de trabajo; la lista contiene seis cargos.*

## 3.8 Facturas y archivos PDF

- Facturas de cliente: abrir **Contabilidad → Clientes → Facturas** (enlace administrativo `/odoo/accounting/1/invoicing`).
- Facturas de proveedor: abrir **Contabilidad → Proveedores → Facturas** (enlace `/odoo/accounting/2/bills`).
- Para emitir un PDF manualmente: abrir una factura publicada, elegir **Imprimir** y seleccionar el reporte de factura.
- La carpeta local con los 50 PDF generados para la entrega es `outputs/facturas_pdf/`. El repositorio conserva un archivo por factura; por ejemplo, [`factura_quetzalmart_001.pdf`](../outputs/facturas_pdf/factura_quetzalmart_001.pdf).
- El complemento propio `quetzalmart_invoice_dms` archiva automáticamente en Odoo DMS el PDF oficial de una factura de cliente o proveedor después de publicarla. El destino es **Documentos QuetzalMart → Facturas PDF**; el archivo queda categorizado y etiquetado por tipo y año.
- Los 50 PDF existentes se incorporan al mismo archivo documental con `infra/archive_existing_invoices_to_dms.py`. La carpeta `outputs/facturas_pdf/` conserva además la copia del proyecto para entregar; no es la carpeta interna de Odoo.
- Para verificar una factura nueva: publicarla, abrir **Documentos**, entrar a **Facturas PDF** y buscar el nombre de la factura. La prueba automatizada está descrita en `infra/test_invoice_dms_auto_archive.py`; el módulo y su instalador están en `infra/odoo_addons/quetzalmart_invoice_dms/` e `infra/install_invoice_dms_module.sh`.

![Listado de facturas de cliente en Odoo](../capturas/manual_1/20_facturas_cliente_listado_163.png)

*Figura 17. Listado de facturas de cliente; la vista muestra 163 registros y sus estados.*

![Detalle de la factura INV/2026/00163](../capturas/manual_1/21_factura_detalle_INV_2026_00163.png)

*Figura 18. Factura de cliente `INV/2026/00163`, vinculada a la venta `S00178`, con total de Q75,89 y estado pagado.*

## 3.9 Correos y documentos

Las plantillas transaccionales y la campaña se consultan desde las aplicaciones de Ventas/Facturación y Marketing por correo. En el entorno de demostración, Mailpit sirve como buzón local de pruebas. La evidencia de Mailpit demuestra que Odoo generó y entregó el correo al capturador local; **no demuestra entrega a Gmail ni a un servidor SMTP externo**.

![Bandeja real de Mailpit con mensajes de prueba de QuetzalMart](../capturas/manual_1/13_correo_mailpit.png)

*Figura 19. Bandeja de Mailpit con mensajes de prueba. Es evidencia interna de generación/captura, no de recepción externa.*

Para documentos, abrir la aplicación OCA DMS y clasificar cada archivo en su carpeta/categoría, usando etiquetas para facilitar la búsqueda. La existencia de PDFs no convierte un contrato en firmado: los contratos del proyecto deben identificarse como simulados y no firmados.

![Archivos y categorías de Odoo Documentos](../capturas/manual_1/22_documentos_archivos_y_categorias.png)

*Figura 20. Vista de OCA DMS con 75 archivos y categorías visibles: 5 contratos de empleado, 5 de outsourcing, 60 facturas de cliente y 5 facturas de proveedor.*

---

# 4. RPA de UiPath: flujo, evidencia y ventajas

## 4.1 Objetivo y límites

El robot automatiza la lectura de hojas Excel del auxiliar y ejecuta las importaciones a través de las pantallas de Odoo. El flujo principal está en `rpa/QuetzalMart_RPA/Main.xaml`; dependencias y versión se describen en `rpa/QuetzalMart_RPA/project.json`.

El RPA **no usa una API de Odoo**, no ejecuta SQL y no escribe directamente en PostgreSQL. La carga de inventario también usa la interfaz de Odoo. Esta decisión respeta la indicación del auxiliar para la evaluación.

## 4.2 Preparación y ejecución

1. Abrir el proyecto `rpa/QuetzalMart_RPA` en UiPath Studio.
2. Confirmar que estén disponibles `UiPath.Excel.Activities 3.6.1`, `UiPath.System.Activities 25.10.3` y `UiPath.UIAutomation.Activities 26.10.4`.
3. Abrir Chrome, iniciar sesión en Odoo y dejar habilitada la extensión UiPath.
4. Ejecutar `Main.xaml`.
5. Cuando el robot solicite la carpeta raíz, seleccionar `datos\prueba_rpa\lote_auxiliar` para la prueba preparada. En la evaluación se selecciona la carpeta entregada por el auxiliar.
6. El flujo recorre subcarpetas, identifica libros Excel y procesa las hojas que tengan exactamente los nombres `clientes` y `productos`.
7. El robot elimina filas vacías, valida datos obligatorios, prepara un Excel temporal con la hoja que se va a importar y abre la pantalla de importación de Odoo.
8. En cada importación revisa el resultado de **Probar** antes de confirmar **Importar**.
9. Para las cantidades físicas, el flujo prepara la columna de conteo y navega a **Ajustes de inventario**. Después de importar, aplica el ajuste, reemplaza el motivo predeterminado por el motivo configurado y pulsa **Actualizar cantidades**.
10. Al terminar, revisar el panel **Salida** de UiPath y verificar en Odoo que los registros quedaron guardados. El aviso final del robot, por sí solo, no reemplaza esta comprobación.

![UiPath solicita seleccionar la carpeta raíz de los Excel](../capturas/manual_1/09_rpa_solicitud_carpeta.png)

*Figura 21. Diálogo de UiPath para seleccionar la carpeta que contiene los archivos del auxiliar.*

![Secuencia del flujo UiPath para navegar a Contactos e importar](../capturas/manual_1/10_rpa_flujo_importacion.png)

*Figura 22. Captura del diseñador UiPath con la secuencia de apertura de Contactos y su flujo de importación.*

![Pantalla de Odoo usada por el RPA para importar productos](../capturas/manual_1/11_importacion_productos_odoo.png)

*Figura 23. El RPA ejecuta la importación en la interfaz web; la captura no proviene de una llamada API.*

![El flujo termina y solicita validar los registros en Odoo](../capturas/manual_1/12_rpa_fin_flujo.png)

*Figura 24. Mensaje final del flujo: indica expresamente que aún se deben validar los registros en Odoo. El resultado de contactos importados se muestra en la Figura 4.*

### Secuencia ampliada del flujo en UiPath

Las siguientes capturas muestran el diseño del flujo de extremo a extremo: selección de carpeta, recorrido de libros, preparación de las hojas, navegación por la interfaz de Odoo, importación de clientes y productos y confirmación de los ajustes de inventario. Las capturas son del diseñador de UiPath; la validación de los datos cargados se complementa con las Figuras 4, 14–18 y 20.

![Figura 25. Solicitud de carpeta raíz en UiPath](../capturas/manual_1/24_parte1_rpa_solicitar_carpeta.png)

*Figura 25. El flujo solicita la carpeta raíz que contiene los Excel y registra el inicio del recorrido.*

![Figura 26. Recorrido recursivo de libros Excel](../capturas/manual_1/24_parte2_rpa_recorre_excel.png)

*Figura 26. Recorrido de archivos Excel y preparación de la lectura de sus hojas.*

![Figura 27. Lectura de estructura y búsqueda de hojas requeridas](../capturas/manual_1/24_parte3_rpa_recorre_excel.png)

*Figura 27. Lectura del libro y comprobación de las hojas con los nombres requeridos.*

![Figura 28. Preparación del archivo temporal de clientes](../capturas/manual_1/24_parte4_rpa_prepara_excel_clientes.png)

*Figura 28. Preparación de la tabla de clientes que se enviará al importador de Odoo.*

![Figura 29. Inicio de navegación para importar clientes](../capturas/manual_1/24_parte5_rpa_flujo_clientes.png)

*Figura 29. Secuencia de UiPath que abre la pantalla de Contactos y comienza la importación de clientes.*

![Figura 30. Flujo de importación de clientes, parte 6](../capturas/manual_1/24_parte6_rpa_flujo_clientes.png)

*Figura 30. Continuación de la secuencia de importación de clientes en la interfaz de Odoo.*

![Figura 31. Flujo de importación de clientes, parte 7](../capturas/manual_1/24_parte7_rpa_flujo_clientes.png)

*Figura 31. Acciones de UiPath para seleccionar y configurar la importación de clientes.*

![Figura 32. Flujo de importación de clientes, parte 8](../capturas/manual_1/24_parte8_rpa_flujo_clientes.png)

*Figura 32. Continuación de las acciones de importación de clientes.*

![Figura 33. Flujo de importación de clientes, parte 9](../capturas/manual_1/24_parte9_rpa_flujo_clientes.png)

*Figura 33. Secuencia de validación y confirmación de la importación de clientes.*

![Figura 34. Flujo de importación de clientes, parte 10](../capturas/manual_1/24_parte10_rpa_flujo_clientes.png)

*Figura 34. Paso de confirmación de la importación de clientes mediante el importador web de Odoo.*

![Figura 35. Inicio de lectura y validación de productos](../capturas/manual_1/24_parte11_rpa_flujo_productos.png)

*Figura 35. El flujo detecta la hoja `productos`, limpia filas vacías y valida los campos requeridos.*

![Figura 36. Flujo de importación de productos, parte 12](../capturas/manual_1/24_parte12_rpa_flujo_productos.png)

*Figura 36. Continuación de las validaciones y preparación de los datos de productos.*

![Figura 37. Flujo de importación de productos, parte 13](../capturas/manual_1/24_parte13_rpa_flujo_productos.png)

*Figura 37. Preparación de los campos de producto para la importación.*

![Figura 38. Flujo de importación de productos, parte 14](../capturas/manual_1/24_parte14_rpa_flujo_productos.png)

*Figura 38. Continuación de la secuencia de importación de productos.*

![Figura 39. Flujo de importación de productos, parte 15](../capturas/manual_1/24_parte15_rpa_flujo_productos.png)

*Figura 39. Configuración de acciones en la interfaz de Odoo para productos.*

![Figura 40. Flujo de importación de productos, parte 16](../capturas/manual_1/24_parte16_rpa_flujo_productos.png)

*Figura 40. Continuación de la interacción automatizada con la pantalla de productos.*

![Figura 41. Flujo de importación de productos, parte 17](../capturas/manual_1/24_parte17_rpa_flujo_productos.png)

*Figura 41. Acciones de UiPath para completar la carga de productos.*

![Figura 42. Flujo de importación de productos, parte 18](../capturas/manual_1/24_parte18_rpa_flujo_productos.png)

*Figura 42. Continuación de la automatización de productos y su proceso de importación.*

![Figura 43. Flujo de importación de productos, parte 19](../capturas/manual_1/24_parte19_rpa_flujo_productos.png)

*Figura 43. Pasos finales de la carga de productos en Odoo.*

![Figura 44. Flujo de importación de productos, parte 20](../capturas/manual_1/24_parte20_rpa_flujo_productos.png)

*Figura 44. Acciones asociadas a la aplicación de cantidades de inventario.*

![Figura 45. Flujo de importación de productos, parte 21](../capturas/manual_1/24_parte21_rpa_flujo_productos.png)

*Figura 45. El flujo sustituye el motivo predeterminado del ajuste y pulsa **Actualizar cantidades** para confirmar.*

## 4.3 Validaciones importantes

- Procesar únicamente hojas con nombres exactos `clientes` y `productos`; las variaciones de mayúsculas, espacios o tildes no son equivalentes.
- No importar nombres obligatorios vacíos.
- Dejar vacías las columnas opcionales sin dato en vez de insertar texto ficticio.
- No asignar “cantidad a la mano” a productos tipo servicio; el control de existencias corresponde a productos almacenables.
- Las columnas de relaciones, por ejemplo compañía o etiquetas, deben coincidir con valores reconocidos por Odoo. Si una referencia no existe, resolverla antes de importar.
- Si **Probar** devuelve un error, no confirmar la importación: corregir el Excel o su mapeo y probar de nuevo.
- Al trabajar con inventario, escribir el motivo sustituyendo el texto por defecto y confirmar con **Actualizar cantidades**. No basta con llegar a la pantalla ni pulsar **Aplicar todo** si aparece el diálogo de motivo.
- El flujo está ligado a selectores de Chrome; mantener Chrome como navegador de ejecución y no cambiarlo a Brave durante la ejecución.

## 4.4 Ventajas de implementar el RPA

- Reduce la repetición manual de abrir libros, localizar hojas y cargar archivos.
- Procesa varias carpetas y libros en un mismo recorrido.
- Estandariza la carga por medio del importador oficial de Odoo.
- Reduce errores por filas vacías, valores requeridos ausentes y tipos de producto incompatibles con inventario.
- Deja registros de avance en la salida de UiPath y permite validar los datos en el ERP.
- No expone credenciales de base de datos ni requiere acceso directo a PostgreSQL.
- Hace que el proceso sea demostrable: archivo de entrada → lectura y validación → importación web → verificación en Odoo.

## 4.5 Resultado de la prueba del proyecto

El equipo reportó la ejecución final del RPA con la carpeta exacta `datos\prueba_rpa\lote_auxiliar` y comprobó en Odoo los registros de prueba de clientes `PRUEBA SS 1`, `PRUEBA SS 2`, `PRUEBA SS 3` y `PRUEBA SS 4`. Para comprobar una ejecución, revisar la salida de UiPath, buscar los nombres cargados en Contactos y las referencias en Productos, y contrastar las fichas con el Excel. Si el lote contiene existencias, revisar y aplicar solo sus ajustes con el motivo correspondiente.

---

# 5. Comprobación de resultados

1. Confirmar que Odoo y el sitio web respondan por HTTPS.
2. Comparar los registros importados con el archivo de entrada y revisar nombres, referencias y relaciones.
3. Comprobar el estado de las órdenes; una cotización no equivale a una orden confirmada.
4. Revisar recepciones, entregas, cantidades y ajustes de inventario del lote.
5. Comprobar facturas publicadas, PDF y clasificación en DMS.
6. Consultar el registro de ejecución de UiPath y comprobar los clientes y productos cargados.

El Anexo B muestra el acceso y la validación de archivos por módulo. **Probar** comprueba el archivo; **Importar** guarda el lote. Los ejemplos de validación no acreditan por sí solos una importación guardada.

---

## Referencias locales del proyecto

- Infraestructura: `infra/`.
- Datos maestros: `infra/seed_block4.py`.
- Ventas y compras: `infra/seed_block5.py`.
- Portal web: `infra/seed_block6.py` y `assets/brand/`.
- Google Analytics: `infra/seed_block7_ga4.py`.
- Robot: `rpa/QuetzalMart_RPA/Main.xaml`.
- Pruebas del RPA: `datos/prueba_rpa/lote_auxiliar/`.
- Consultas de verificación: `consultas_sql/`.
- PDFs de factura: `outputs/facturas_pdf/`.
- Evidencia digital DMS: `outputs/dms_verified/`.
- Capturas de este manual: `capturas/manual_1/`.


# Anexo B - Carga de información por módulo

Las capturas del 7 de octubre de 2026 muestran acceso, mapeo y validación de archivos de dos registros. No representan una importación guardada. Cargar primero las relaciones maestras; conservar identificadores externos estables al actualizar.

## B01 - Departamentos

1. Abrir **Empleados > Departamentos**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Crear los departamentos antes de asociarlos a empleados. Ejemplo: MANUAL Departamento 01.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Departamentos](capturas/2026-10-07/departamentos_01_acceso.jpg)

*Figura B01.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Nombre del departamento |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar el nombre cargado en Departamentos; abrirlo y comprobar su denominación y compañía.

![Validación de Departamentos](capturas/2026-10-07/departamentos_02_validacion.jpg)

*Figura B01.2. Mapeo y validación sin guardar el lote.*

## B02 - Puestos de trabajo

1. Abrir **Empleados > Configuración > Puestos de trabajo**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Preparar un registro por puesto. Si se asigna Departamento, utilizar un departamento existente.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Puestos de trabajo](capturas/2026-10-07/cargos_01_acceso.jpg)

*Figura B02.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Puesto de trabajo |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL Puesto 01 y comprobar nombre y departamento. La carga del puesto no crea empleados.

![Validación de Puestos de trabajo](capturas/2026-10-07/cargos_02_validacion.jpg)

*Figura B02.2. Mapeo y validación sin guardar el lote.*

## B03 - Empleados

1. Abrir **Empleados > Empleados**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. El ejemplo valida dos fichas mínimas. Para la carga de personal, añadir correo laboral, puesto y departamento; resolver primero las relaciones.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Empleados](capturas/2026-10-07/empleados_01_acceso.jpg)

*Figura B03.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `External ID` | ID externo |
| `Name` | Nombre del empleado |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL Empleado 01 y comprobar la ficha. Verificar puesto y departamento si se incluyeron en el archivo.

![Validación de Empleados](capturas/2026-10-07/empleados_02_validacion.jpg)

*Figura B03.2. Mapeo y validación sin guardar el lote.*

## B04 - Clientes y proveedores

1. Abrir **Contactos**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Clientes y proveedores comparten el directorio de Contactos. Añadir correo, teléfono, país e identificación fiscal cuando correspondan; usar etiquetas existentes para clasificar.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Clientes y proveedores](capturas/2026-10-07/contactos_01_acceso.jpg)

*Figura B04.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Nombre |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL Contacto 01 y abrir la ficha. Comprobar nombre, datos incluidos y clasificación; no confundir un contacto con una oportunidad de CRM.

![Validación de Clientes y proveedores](capturas/2026-10-07/contactos_02_validacion.jpg)

*Figura B04.2. Mapeo y validación sin guardar el lote.*

## B05 - Oportunidades de CRM

1. Abrir **CRM > Mi flujo**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Preparar una oportunidad por fila. Para asociar Cliente, Etapa o Comercial, usar contactos, etapas y usuarios existentes.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Oportunidades de CRM](capturas/2026-10-07/crm_01_acceso.jpg)

*Figura B05.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Oportunidad |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL Oportunidad 01 en CRM. Abrirla y comprobar cliente, etapa y responsable cuando se hayan importado.

![Validación de Oportunidades de CRM](capturas/2026-10-07/crm_02_validacion.jpg)

*Figura B05.2. Mapeo y validación sin guardar el lote.*

## B06 - Productos

1. Abrir **Inventario > Productos > Productos**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. El ejemplo usa consu (Bienes), seguimiento True, referencia MANUAL-PRD-01, precio 15 y costo 8. Mantener códigos de barras como texto para conservar los ceros iniciales.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Productos](capturas/2026-10-07/productos_01_acceso.jpg)

*Figura B06.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Nombre |
| `Referencia interna` | Referencia interna |
| `Tipo de producto` | Tipo de producto |
| `Rastrear inventario` | Rastrear inventario |
| `Código de barras` | Código de barras |
| `Precio de venta` | Precio de venta |
| `Coste` | Costo |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL-PRD-01; comprobar tipo, seguimiento, referencia, precio, costo y código de barras. Importar productos no equivale a cargar existencias físicas.

![Validación de Productos](capturas/2026-10-07/productos_02_validacion.jpg)

*Figura B06.2. Mapeo y validación sin guardar el lote.*

## B07 - Inventario físico

1. Abrir **Inventario > Operaciones > Inventario físico**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Los productos y ubicaciones deben existir. El ejemplo usa AUDIT-PRD-20261006-1, GT/Stock y cantidad contada 4. La cantidad es absoluta. Para actualizar líneas existentes, exportar y reutilizar sus ID externos.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Inventario físico](capturas/2026-10-07/inventario_01_acceso.jpg)

*Figura B07.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Product` | Producto |
| `Ubicación` | Ubicación |
| `Cantidades contadas` | Cantidades contadas |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Revisar solo las líneas del lote, cantidades contadas y diferencia. Aplicar el ajuste seleccionado, reemplazar el motivo predeterminado y confirmar Actualizar cantidades. Comprobar la existencia final en GT/Stock.

![Validación de Inventario físico](capturas/2026-10-07/inventario_02_validacion.jpg)

*Figura B07.2. Mapeo y validación sin guardar el lote.*

## B08 - Cotizaciones de venta

1. Abrir **Ventas > Órdenes > Cotizaciones**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Cargar primero clientes y productos. Ejemplo: Cliente QuetzalMart 01, producto QM-001, cantidad 2 y precio 13.56. Cada fila del ejemplo contiene una cotización con una línea.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Cotizaciones de venta](capturas/2026-10-07/ventas_01_acceso.jpg)

*Figura B08.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Referencia de la orden |
| `Cliente` | Cliente |
| `order_line/product_id` | Líneas de la orden / Producto |
| `order_line/product_uom_qty` | Líneas de la orden / Cantidad |
| `order_line/price_unit` | Líneas de la orden / Precio unitario |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL-VENTAS-01; comprobar cliente, líneas e impuestos. La importación crea cotizaciones: confirmar la aceptada para convertirla en pedido y continuar con entrega y facturación.

![Validación de Cotizaciones de venta](capturas/2026-10-07/ventas_02_validacion.jpg)

*Figura B08.2. Mapeo y validación sin guardar el lote.*

## B09 - Solicitudes de compra

1. Abrir **Compras > Órdenes > Solicitudes de cotización**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Cargar primero proveedores y productos. Ejemplo: Proveedor Regional 01, QM-001, cantidad 2 y precio 13.56. Cada fila del ejemplo contiene una solicitud con una línea.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Solicitudes de compra](capturas/2026-10-07/compras_01_acceso.jpg)

*Figura B09.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `Name` | Referencia de la orden |
| `Proveedor` | Proveedor |
| `order_line/product_id` | Líneas de la orden / Producto |
| `order_line/product_qty` | Líneas de la orden / Cantidad |
| `order_line/price_unit` | Líneas de la orden / Precio unitario |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL-COMPRAS-01; revisar proveedor, líneas e impuestos. Confirmar la solicitud aprobada para obtener la orden; validar después su recepción y generar la factura vinculada.

![Validación de Solicitudes de compra](capturas/2026-10-07/compras_02_validacion.jpg)

*Figura B09.2. Mapeo y validación sin guardar el lote.*

## B10 - Facturas de cliente

1. Abrir **Facturación > Clientes > Facturas**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Importar desde la vista Facturas para usar el tipo de cliente. Ejemplo: Cliente QuetzalMart 01, fecha 2026-10-07, QM-001, cantidad 2 y precio 13.56. Revisar diario, cuentas e impuestos antes de publicar.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Facturas de cliente](capturas/2026-10-07/facturas_cliente_01_acceso.jpg)

*Figura B10.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `partner_id` | Contacto |
| `invoice_date` | Fecha de la factura |
| `invoice_line_ids/product_id` | Líneas de factura / Producto |
| `invoice_line_ids/name` | Líneas de factura / Etiqueta |
| `invoice_line_ids/quantity` | Líneas de factura / Cantidad |
| `invoice_line_ids/price_unit` | Líneas de factura / Precio unitario |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Filtrar por cliente y fecha, abrir el borrador y comprobar líneas y total. Publicar únicamente después de revisar; verificar el número contable y el PDF. Para facturar pedidos existentes, generar la factura desde el pedido y evitar duplicarla por importación.

![Validación de Facturas de cliente](capturas/2026-10-07/facturas_cliente_02_validacion.jpg)

*Figura B10.2. Mapeo y validación sin guardar el lote.*

## B11 - Facturas de proveedor

1. Abrir **Facturación > Proveedores > Facturas de proveedor**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Importar desde Facturas de proveedor para usar el tipo correcto. Ejemplo: Proveedor Regional 01, fecha 2026-10-07 y producto QM-001. Añadir la referencia de proveedor del documento real cuando corresponda.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Facturas de proveedor](capturas/2026-10-07/facturas_proveedor_01_acceso.jpg)

*Figura B11.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `partner_id` | Contacto |
| `invoice_date` | Fecha de la factura |
| `invoice_line_ids/product_id` | Líneas de factura / Producto |
| `invoice_line_ids/name` | Líneas de factura / Etiqueta |
| `invoice_line_ids/quantity` | Líneas de factura / Cantidad |
| `invoice_line_ids/price_unit` | Líneas de factura / Precio unitario |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar por proveedor y fecha; revisar borrador, referencia, diario, cuentas, impuestos y total antes de publicar. Para compras existentes, usar Crear factura desde la orden para conservar el vínculo y evitar duplicados.

![Validación de Facturas de proveedor](capturas/2026-10-07/facturas_proveedor_02_validacion.jpg)

*Figura B11.2. Mapeo y validación sin guardar el lote.*

## B12 - Contratos de empleados

1. Abrir **Empleados > Empleados > Contratos**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Los empleados deben existir. El ejemplo valida contratos en estado Nuevo asociados a Ana López, con fecha 2026-10-07 y salario 4500. Revisar vigencia, horario y compañía antes de activar un contrato.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Contratos de empleados](capturas/2026-10-07/contratos_01_acceso.jpg)

*Figura B12.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `name` | Referencia del contrato |
| `employee_id` | Empleado |
| `date_start` | Fecha de inicio |
| `wage` | Salario |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL-CONTRATO-01; comprobar empleado, fecha, salario y estado. Revisar que no se solape con otro contrato activo. La ficha interna no sustituye al PDF contractual firmado; los documentos del proyecto son simulados.

![Validación de Contratos de empleados](capturas/2026-10-07/contratos_02_validacion.jpg)

*Figura B12.2. Mapeo y validación sin guardar el lote.*

## B13 - Destinatarios de Marketing

1. Abrir **Marketing por correo > Listas de correo > Contactos de la lista de correo**, el menú de engranaje y **Importar registros**.
2. Preparar CSV UTF-8 o Excel con encabezados e ID externo estable. Preparar una fila por destinatario y revisar duplicados. El ejemplo usa manual01@example.invalid, una dirección reservada para documentación; no usarla para enviar campañas.
3. Pulsar **Subir archivo de datos** y utilizar la primera fila como encabezado.

![Acceso a Destinatarios de Marketing](capturas/2026-10-07/marketing_01_acceso.jpg)

*Figura B13.1. Acceso real a la importación.*

| Columna | Campo de Odoo |
|---|---|
| `ID externo` | ID externo |
| `name` | Nombre |
| `email` | Correo electrónico |

4. Revisar el mapeo de cada columna y pulsar **Probar**. Corregir errores y repetir hasta obtener **Todo parece correcto.**
5. Con el lote definitivo validado, pulsar **Importar** y esperar la finalización.
6. Buscar MANUAL Destinatario 01; comprobar el correo y asociar la lista de correo correspondiente. Revisar consentimiento y exclusiones antes de seleccionar destinatarios. Importar contactos no envía una campaña.

![Validación de Destinatarios de Marketing](capturas/2026-10-07/marketing_02_validacion.jpg)

*Figura B13.2. Mapeo y validación sin guardar el lote.*

## B14 - Documentos DMS

1. Preparar los PDF por grupo y usar nombres identificables, por ejemplo `INV_2026_00154.pdf`.
2. Abrir **Documentos > Archivos** y pulsar **Subir**. Esta acción carga archivos binarios, no registros CSV.
3. Seleccionar los archivos del lote, revisar la subida y clasificar cada documento.

![Acceso a Documentos DMS](capturas/2026-10-07/dms_01_acceso.jpg)

*Figura B14.1. Vista Archivos y acción Subir. No se cargaron documentos para esta captura.*

4. Consultar **Documentos > Carpetas > Documentos QuetzalMart**. Los destinos son Contratos de empleados, Contratos de outsourcing, Facturas PDF y Facturas de proveedores.
5. Buscar los nombres del lote, comprobar carpeta, categoría y etiquetas y abrir una muestra. Comparar el número de archivos esperado con el incorporado.

![Carpetas DMS](capturas/2026-10-07/dms_02_carpetas.jpg)

*Figura B14.2. Carpetas y conteos consultados el 7 de octubre de 2026.*

Para facturas de Odoo, usar el archivado inicial y automático descrito en 1.5; evitar cargar otra vez un PDF ya archivado. Los contratos del proyecto son borradores académicos sin firma.

## B15 - Catálogo del sitio web

1. Cargar productos mediante el procedimiento B06. El sitio utiliza las mismas fichas del ERP.
2. Revisar nombre, precio, imagen, categoría y disponibilidad; publicar los artículos destinados a la tienda mediante las opciones del sitio web de su ficha.
3. Abrir `/shop`, buscar una muestra y comprobar la ficha pública. Si falta un artículo, revisar su publicación y los filtros del catálogo.

![Catálogo público](../capturas/manual_1/02_catalogo_productos.png)

*Figura B15.1. Captura original del catálogo conservada del manual.*

Importar productos y publicarlos son pasos separados. Los eventos y audiencias de GA4 se documentan en el Manual 3.

---

# Anexo C - Enlaces de acceso al proyecto

El ERP/CRM y el sitio web utilizan la misma instalación de Odoo.

## C01 / Sitio web

[https://quetzalmart.34-9-149-41.sslip.io](https://quetzalmart.34-9-149-41.sslip.io)

Inicio del portal público de QuetzalMart.

## C02 / Tienda en línea

[https://quetzalmart.34-9-149-41.sslip.io/shop](https://quetzalmart.34-9-149-41.sslip.io/shop)

Catálogo, fichas de productos y acceso al carrito de compras.

## C03 / ERP y CRM - Odoo

[https://quetzalmart.34-9-149-41.sslip.io/odoo](https://quetzalmart.34-9-149-41.sslip.io/odoo)

Inicio de sesión y menú de aplicaciones: Ventas, Compras, Inventario, Facturación, Contactos, CRM, Empleados, Marketing y Documentos. Requiere una cuenta autorizada en Odoo.

## C04 / Google Analytics 4

[https://analytics.google.com/analytics/web/#/a408877368p555190935/realtime/overview](https://analytics.google.com/analytics/web/#/a408877368p555190935/realtime/overview)

Propiedad QuetzalMart Web 2026 (555190935), cuenta 408877368. El enlace abre Tiempo real; los informes y exploraciones del Manual 3 se consultan desde el menú de GA4. Requiere permiso de acceso a esta propiedad.

## C05 / Repositorio del proyecto

[https://github.com/DavidVelasquez77/GEREN2_PROYECTO_G1](https://github.com/DavidVelasquez77/GEREN2_PROYECTO_G1)

Fuentes del proyecto, infraestructura, consultas SQL, datos, evidencias y manuales. Para recursos privados, usar una cuenta con acceso al repositorio.

## C06 / Proyecto de UiPath

[https://github.com/DavidVelasquez77/GEREN2_PROYECTO_G1/tree/main/rpa/QuetzalMart_RPA](https://github.com/DavidVelasquez77/GEREN2_PROYECTO_G1/tree/main/rpa/QuetzalMart_RPA)

Carpeta del robot en el repositorio. Para ejecutarlo, descargar el proyecto, abrir project.json en UiPath Studio, restaurar dependencias y ejecutar Main.xaml. La ejecución se realiza en Windows.
