# Bloque 4 — Configuración funcional y datos base

## Resultado

Odoo Community 18 quedó preparado como instancia central de QuetzalMart. La configuración y los datos de este bloque residen en la única base PostgreSQL `quetzalmart` desplegada en la VM de Google Cloud.

Tienda pública: <https://quetzalmart.34-9-149-41.sslip.io/shop>

## Aplicaciones instaladas

| Área | Módulo técnico |
|---|---|
| Ventas | `sale_management` |
| Compras | `purchase_stock` |
| Inventario | `stock` |
| Facturación y contabilidad | `account` |
| Empleados | `hr` |
| Contratos | `hr_contract` |
| CRM | `crm` |
| Comercio electrónico | `website_sale` |
| Marketing por correo | `mass_mailing` |
| Localización de Guatemala | `l10n_gt` |
| Documentos Community | `dms` |
| Pago de prueba | `payment_demo` |

Odoo Community no incluye la aplicación empresarial Documentos. Para cubrir la gestión documental sin cambiar de edición se instaló OCA DMS 18.0 desde su repositorio oficial y se agregó `/mnt/extra-addons/oca-dms` a `addons_path`.

## Organización

- Compañía: QuetzalMart.
- País: Guatemala.
- Moneda principal: quetzal guatemalteco (GTQ).
- Idioma de operación: español latinoamericano (`es_419`).
- Monedas adicionales activas: USD y MXN.
- Almacenes: Sucursal Guatemala (`GT`), Sucursal México (`MX`) y Sucursal El Salvador (`SV`).

## Datos maestros creados

| Elemento | Cantidad |
|---|---:|
| Departamentos activos | 5 |
| Puestos | 6 |
| Empleados activos | 35 |
| Contratos | 35 |
| Clientes | 30 |
| Proveedores | 25 |
| Productos QuetzalMart | 60 |
| Almacenes | 3 |

Los productos usan referencias consecutivas desde `QM-001` hasta `QM-060`, incluyen código de barras, categoría, costo, precio de venta e IVA del 12 %, y están publicados en el comercio electrónico.

## Inventario inicial

| Almacén | Unidades |
|---|---:|
| Sucursal Guatemala | 4,800 |
| Sucursal México | 3,300 |
| Sucursal El Salvador | 2,700 |

Cada producto tiene 80 unidades en Guatemala, 55 en México y 45 en El Salvador.

## Sitio web y pagos

- Catálogo público con 60 productos y categorías Abarrotes, Bebidas, Limpieza, Hogar, Cuidado personal y Tecnología.
- Moneda y precios visibles en GTQ.
- Paginación predeterminada de 20 productos por página.
- Proveedor de pago Demo habilitado en modo de prueba. Su evento de compra se verificará con Google Analytics 4 en el bloque correspondiente; si GA4 no lo reconoce, se configurará una pasarela real, según la aclaración del auxiliar.

## Gestión documental

Se creó el almacenamiento `Documentos QuetzalMart` y una estructura inicial con un directorio raíz y tres directorios de clasificación. Las categorías y etiquetas quedan listas para vincular documentos durante los bloques transaccionales.

## Automatización y reproducción

- `infra/preconfigure_quetzalmart.py`: ajustes previos de compañía y localización.
- `infra/install_block4_modules.sh`: instalación de módulos.
- `infra/seed_block4.py`: creación idempotente de datos maestros y configuración.
- `infra/run_block4_seed.sh`: ejecución del sembrado dentro del contenedor de Odoo.
- `consultas_sql/bloque4_verificacion.sql`: consultas de comprobación para la evaluación.

UiPath no intervino en esta carga inicial. El robot obligatorio de clientes y productos se construirá en su bloque y operará exclusivamente mediante la interfaz gráfica de Odoo, sin API, como indicó el auxiliar.

## Criterio de cierre

El bloque queda cerrado porque los módulos están instalados, los conteos coinciden con la planificación, existen tres almacenes en una sola compañía, el inventario está distribuido y el catálogo público responde por HTTPS. Las transacciones masivas no pertenecen a este bloque; se crearán en el bloque 5.
