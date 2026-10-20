# Análisis del enunciado y matriz de cumplimiento

Enunciado: *Proyecto Segundo Semestre 2026* (SOG2, 35 pts). Empresa: **QuetzalMart**, cadena de
tiendas con sede en Guatemala que abre sucursales en **México** y **El Salvador** y necesita ERP,
tienda en línea, analítica, gestión documental, RPA y marketing digital.

## Requisitos para optar a la calificación (si falta uno, la nota es 0)

| Requisito | Estado en este proyecto |
|---|---|
| Entregar los 3 manuales en PDF | Generados por `manuales/construir_manuales.py`. Falta: datos del grupo, capturas de la nube, de UiPath y de GA4, y cifras reales de GA4 (Manual 3). |
| Entrega en UEDI a tiempo | Responsabilidad del grupo. |
| ERP implementado en la nube | `nube/instalar.sh` en una VM de Azure o Google Cloud. |
| Consultas SQL preparadas y base en la nube | `sql/consultas_calificacion.sql` (probadas) y PostgreSQL en la VM. |
| Sin copias parciales ni totales | Todo el código, datos, diseño e imágenes de esta carpeta son propios; el proyecto de referencia no se reutilizó. |

## Requisitos funcionales

| # | Requisito | Dónde está | Cómo se verifica |
|---|---|---|---|
| 1a | 150 ventas, distintos productos y clientes, en BD | `cargar_quetzalmart.py --paso transacciones` | SQL 1.1-1.3 |
| 1b | 20 cotizaciones a clientes y proveedores | 20 de venta + 20 de compra | SQL 2.1-2.3 |
| 2 | 35 empleados, 6 cargos, 5 departamentos | Plantillas 01-04 | SQL 3.1-3.3 |
| 3a | 100 compras con sus facturas | Transacciones (recepción + factura publicada) | SQL 4.1-4.2 |
| 3b | 60 materiales para las sucursales | Plantilla 08 + existencias por sucursal | SQL 5.1-5.2 |
| 4 | 50 facturas; carpeta con los PDF (+ los de la calificación) | `qm_gestion_documental` archiva cada factura publicada | SQL 6.1-6.3, Documentos |
| Web | Catálogo, carrito (IVA y envío), pago, factura, conectado a ERP y CRM | `qm_implementacion`, `qm_crm_postventa` | Compra de prueba |
| GA4 | Eventos `view_item`, `add_to_cart`, `begin_checkout`, `purchase` | Odoo + `qm_ga4_ecommerce` | Tiempo real / DebugView |
| GA4 | Conversión, adquisición, ingresos, más vendidos, abandono | Informes y exploraciones | `docs/03_google_analytics.md` |
| GA4 | 3 segmentos de usuarios, 5 de eventos, 2 exploraciones, 3 audiencias (1 personalizada) | Configuración en GA4 (manual) | Manual 3 |
| DMS | 5 facturas de proveedores, 5 contratos de outsourcing, 5 contratos de empleados, con etiquetas | OCA DMS + paso `documentos` | SQL 12 |
| RPA | Recorrer carpetas, hojas `clientes`/`productos` en 5.ª posición, cargar a BD; visible en web y BD; ejecutar en la calificación | `rpa/QuetzalMart_Robot` + `qm_puente_rpa` | SQL 9, tienda |
| Marketing | Registro al CRM, compra, correo de compra y luego el de marketing, asuntos distintos, remitente no personal | `qm_crm_postventa` + SMTP de la empresa | SQL 11, bandeja |
| Manual 1 | Instalación, módulos, carga masiva con capturas, RPA paso a paso y ventajas | `manuales/manual_1.md` | PDF |
| Manual 2 | Diagramas: UiPath, compras, ventas, flujo del producto, cliente web y tienda | `manuales/manual_2.md` + `diagramas/` | PDF |
| Manual 3 | Inteligencia de negocios con datos de GA4 y gráficas | `manuales/manual_3/` | PDF |

## Decisiones tomadas (confirmar con el auxiliar si hay duda)

1. **PostgreSQL.** El enunciado pone como ejemplo MySQL, Oracle o SQL Server, pero Odoo solo
   funciona con PostgreSQL, que también es relacional.
2. **Cotizaciones:** se hicieron 20 a clientes y además 20 a proveedores.
3. **RPA por la interfaz de Odoo** (Importar registros), sin usar la API, para que la carga se vea
   en la ejecución. Si el libro no trae la hoja en la 5.ª posición, se busca por nombre.
4. **Pago de prueba** (proveedor Demo de Odoo): no se cobran tarjetas reales.
5. **Datos ficticios:** personas, empresas y correos (`.example`) inventados.

## Lo que falta hacer al grupo

- [ ] Crear la VM y ejecutar `nube/instalar.sh` (`docs/01_despliegue_nube.md`).
- [ ] Crear el correo de la empresa y la clave de aplicación (`docs/04_correo_y_marketing.md`).
- [ ] Crear la propiedad GA4, conectarla, generar tráfico y configurar segmentos, exploraciones y
      audiencias (`docs/03_google_analytics.md`).
- [ ] Cargar los datos (`cargar_quetzalmart.py`).
- [ ] Abrir el robot en UiPath Studio, cambiar `urlOdoo` y probarlo (`rpa/README.md`).
- [ ] Completar `manuales/datos_grupo.json`, tomar capturas (`manuales/tomar_capturas.py`, más
      las de la nube, UiPath y GA4), poner las cifras reales en `manual_3/datos_ga4.json` y
      generar los PDF.
