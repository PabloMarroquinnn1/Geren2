# QuetzalMart · Proyecto SOG2, segundo semestre 2026

Implementación propia del caso **QuetzalMart** (cadena de tiendas de Guatemala con sucursales en
México y El Salvador): ERP Odoo 18 en la nube, tienda en línea conectada a Google Analytics 4,
gestión documental, robot de UiPath, CRM y marketing por correo, y los tres manuales.

El análisis del enunciado, la matriz de cumplimiento y la lista de lo que falta hacer están en
[`docs/00_analisis_enunciado.md`](docs/00_analisis_enunciado.md).

## Contenido

| Carpeta | Qué hay |
|---|---|
| `nube/` | Docker Compose (PostgreSQL 16, Odoo 18, Caddy con HTTPS), `instalar.sh`, `actualizar.sh`, `respaldo.sh`, `consola_sql.sh` |
| `odoo_addons/` | Módulos propios: `qm_implementacion` (empresa, sucursales, almacenes, sitio web, envíos), `qm_puente_rpa` (campos que llena el robot), `qm_gestion_documental` (archivo automático de facturas en Documentos), `qm_ga4_ecommerce` (embudo GA4 completo), `qm_crm_postventa` (CRM, correo de compra y campaña con QUETZAL10) |
| `carga_masiva/` | Catálogo de datos, plantillas Excel de importación, imágenes de productos y `cargar_quetzalmart.py` (carga y transacciones por JSON-RPC) |
| `gestion_documental/` | Generador de facturas de proveedor, contratos de outsourcing y contratos laborales en PDF |
| `rpa/` | Robot de UiPath (`QuetzalMart_Robot/`), carpeta de prueba y guía |
| `sql/` | `consultas_calificacion.sql`: una consulta por requisito para mostrar en la calificación |
| `analytics/` | `simular_trafico.py`: visitas y compras con distintos orígenes UTM para GA4 |
| `marca/` | Generador del logotipo, íconos, portada y empaques de los productos |
| `manuales/` | Fuentes de los manuales 1, 2 y 3, diagramas, capturas y `construir_manuales.py` (genera los PDF) |
| `docs/` | Guías paso a paso: nube, carga de datos, GA4, correo y marketing, guion de la calificación |

## Puesta en marcha (resumen)

1. **Nube** ([`docs/01_despliegue_nube.md`](docs/01_despliegue_nube.md)): crear una instancia EC2 de AWS con Ubuntu 24.04
   (c7i-flex.large, 4 GiB, 30 GiB de disco), copiar esta carpeta y ejecutar:

   ```bash
   cd nube
   sudo ./instalar.sh
   ```

   Sin argumento usa `quetzalmart.<ip-pública>.sslip.io`. Crea `.env` con claves aleatorias,
   instala Docker, Odoo, los módulos y el certificado HTTPS, y deja las claves en
   `credenciales.txt`.

2. **Datos** ([`docs/02_carga_de_datos.md`](docs/02_carga_de_datos.md)):

   ```bash
   pip install openpyxl
   python carga_masiva/cargar_quetzalmart.py --url https://SU-DOMINIO --clave CLAVE_ADMIN \
       --ga4 G-XXXXXXXXXX --correo-remitente ventas@SU-EMPRESA \
       --smtp-servidor smtp.gmail.com --smtp-usuario ... --smtp-clave ...
   ```

   Carga 35 empleados, 60 productos, 60 materiales, clientes y proveedores, y genera 150 ventas,
   20 + 20 cotizaciones, 100 compras con factura y los documentos de la gestión documental.

3. **GA4** ([`docs/03_google_analytics.md`](docs/03_google_analytics.md)) y **correo**
   ([`docs/04_correo_y_marketing.md`](docs/04_correo_y_marketing.md)).
4. **RPA** ([`rpa/README.md`](rpa/README.md)): abrir `rpa/QuetzalMart_Robot/project.json` en
   UiPath Studio, ajustar `urlOdoo` y ejecutar con `rpa/carpeta_prueba`.
5. **Manuales**: poner las cifras reales de GA4 en `manuales/manual_3/datos_ga4.json` y ejecutar
   `python manuales/construir_manuales.py` (la portada toma los integrantes de
   `manuales/datos_grupo.json`).

## Requisitos de la calificación

El día de la calificación se sigue [`docs/05_guion_calificacion.md`](docs/05_guion_calificacion.md).
Las consultas SQL se ejecutan con el usuario de solo lectura `consulta` (sus datos quedan en
`nube/credenciales.txt`, que no se sube al repositorio).
