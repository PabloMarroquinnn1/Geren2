# Carga de datos de QuetzalMart

Hay dos formas de cargar la información y ambas usan el **mismo importador de Odoo**:

* **Manual (para las capturas del Manual 1):** cada plantilla de `carga_masiva/plantillas/` se
  importa desde la lista correspondiente con *(engranaje) ► Importar registros ► Subir archivo ►
  Probar ► Importar*. Los encabezados son nombres técnicos de Odoo, así cada columna se relaciona
  sola.
* **Automática:** `carga_masiva/cargar_quetzalmart.py` hace lo mismo por JSON-RPC y además genera
  las transacciones.

## Qué se carga y en qué orden

| # | Plantilla | Dónde se importa en Odoo | Registros |
|---|---|---|---|
| 1 | `01_departamentos.xlsx` | Empleados ► Departamentos | 5 |
| 2 | `02_puestos.xlsx` | Empleados ► Configuración ► Puestos de trabajo | 7 cargos |
| 3 | `03_empleados.xlsx` | Empleados | 35 (con jefe, sucursal, DPI, puesto y departamento) |
| 4 | `04_contratos.xlsx` | Empleados ► Contratos | 35 vigentes |
| 5 | `05_clientes.xlsx` | Contactos | 40 (Guatemala, México y El Salvador) |
| 6 | `06_proveedores.xlsx` | Contactos | 25 proveedores + 5 de outsourcing |
| 7 | `07_productos.xlsx` | Inventario ► Productos | 60 productos de venta publicados |
| 8 | `08_materiales_operativos.xlsx` | Inventario ► Productos | 60 materiales (no se venden) |
| 9 | `09_existencias_iniciales.xlsx` | Inventario ► Inventario físico (luego *Aplicar*) | 360 existencias por sucursal y sector |
| 10 | `10_oportunidades_crm.xlsx` | CRM ► Mi flujo | 18 oportunidades |

Las plantillas se regeneran con `python carga_masiva/generar_plantillas.py` a partir de
`carga_masiva/catalogo.py` (fuente única de nombres, precios, sucursales y personas; todo ficticio).

## Transacciones (paso `transacciones`)

| Requisito del enunciado | Qué genera el script |
|---|---|
| 150 ventas con distintos productos y clientes | 150 pedidos confirmados (`VTA-001`…), entregados desde la sucursal del país del cliente, facturados y 75 % pagados. Fechas entre junio y octubre de 2026. |
| 20 cotizaciones a clientes y proveedores | 20 cotizaciones de venta (`COT-…`, la mitad marcadas como enviadas) **y** 20 solicitudes de cotización a proveedores (`SDC-…`). |
| 100 compras con sus facturas | 100 órdenes de compra confirmadas (`OC-…`), recibidas en la sucursal, con factura del proveedor publicada (`FEL-PRV-…`) y 70 % pagadas. Incluyen compras de materiales operativos. |
| 50 facturas y su PDF en una carpeta | 150 facturas de cliente publicadas; el módulo `qm_gestion_documental` guarda el PDF de cada una en **Documentos ► Archivo QuetzalMart ► Facturas de venta**, también las de la calificación. |

## Comando completo

```bash
pip install openpyxl reportlab
python carga_masiva/cargar_quetzalmart.py --url https://SU-DOMINIO --clave CLAVE_ADMIN [--ga4 ...] [--smtp-...]
```

Pasos: `configurar`, `maestros`, `imagenes`, `existencias`, `crm`, `transacciones`, `documentos`,
`verificar`. Se puede ejecutar uno solo con `--paso NOMBRE`, y repetir sin duplicar (las
plantillas tienen identificador externo y las transacciones se numeran).

El paso `verificar` imprime los mismos conteos que las consultas SQL:

```
[OK ] Ventas confirmadas                         150  (mínimo 150)
[OK ] Cotizaciones de venta                       20  (mínimo 20)
[OK ] Cotizaciones de compra                      20  (mínimo 20)
[OK ] Compras confirmadas                        100  (mínimo 100)
[OK ] Facturas de proveedor publicadas           100  (mínimo 100)
[OK ] Facturas de cliente publicadas             150  (mínimo 50)
[OK ] Empleados                                   36  (mínimo 35)
[OK ] Puestos                                      7  (mínimo 6)
[OK ] Departamentos                                6  (mínimo 5)
[OK ] Materiales operativos                       60  (mínimo 60)
[OK ] Productos publicados en la web              60  (mínimo 60)
[OK ] PDF de facturas en Documentos              150  (mínimo 50)
```

(Empleados y departamentos incluyen el registro del usuario administrador que crea Odoo.)

## Gestión documental (paso `documentos`)

Genera con los datos del ERP y sube al gestor documental, con categoría y etiquetas:

* 5 **facturas de proveedor** (formato FEL), también adjuntas a la factura de proveedor en Odoo.
* 5 **contratos de outsourcing** (seguridad, limpieza, transporte refrigerado, soporte TI,
  control de plagas), adjuntos al proveedor.
* 5 **contratos de trabajo** (Código de Trabajo de Guatemala), adjuntos al empleado.

Los documentos indican que son ficticios y de uso académico.
