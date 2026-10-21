# RPA de QuetzalMart (UiPath)

El robot recorre la carpeta que entrega el auxiliar, encuentra los Excel que traen la hoja
**clientes** o **productos**, junta toda la información en un consolidado por tipo y la carga
en Odoo **usando la pantalla "Importar registros" de Odoo** (no usa la API ni escribe directo
en la base de datos). Al final deja un reporte con lo que procesó.

```
carpeta del auxiliar ──► buscar .xlsx (todas las subcarpetas) ──► listar hojas en orden
        ──► ¿hoja 5 = clientes/productos? (si no, buscar por nombre) ──► leer hoja
        ──► normalizar columnas y valores ──► consolidado_clientes.xlsx / consolidado_productos.xlsx
        ──► Odoo: Subir archivo ► Probar ► Importar ──► reporte_robot.xlsx
```

## Contenido de esta carpeta

| Ruta | Qué es |
|---|---|
| `QuetzalMart_Robot/` | Proyecto de UiPath Studio (abrir `project.json`). |
| `QuetzalMart_Robot/Main.xaml` | Flujo principal: carpeta, búsqueda, hojas, normalización, consolidado, reporte. |
| `QuetzalMart_Robot/ImportarEnOdoo.xaml` | Importa un consolidado con la interfaz de Odoo (Chrome). |
| `carpeta_prueba/` | Carpeta de práctica: libros de 6 hojas, encabezados en inglés y español, duplicados, señuelos. |

## Requisitos en la PC de la calificación

1. **UiPath Studio** (Community sirve) con la extensión de UiPath para **Google Chrome** instalada
   (Studio ► Inicio ► Herramientas ► Extensión de Chrome).
2. Paquetes del proyecto (Studio los descarga solo al abrir): `UiPath.System.Activities`,
   `UiPath.Excel.Activities`, `UiPath.UIAutomation.Activities`. **No hace falta tener Excel
   instalado**: las hojas se leen con las actividades de libro de trabajo.
3. Odoo con los módulos instalados (el módulo `qm_puente_rpa` agrega los campos puente que usa el
   robot) y la interfaz en español.

## Antes de ejecutar

1. Abrir `QuetzalMart_Robot/project.json` en UiPath Studio.
2. En `Main.xaml`, panel **Variables**, cambiar el valor por defecto de `urlOdoo` por la URL de
   su Odoo (por ejemplo `https://quetzalmart.20-55-10-7.sslip.io`, sin `/` al final).
3. Abrir Chrome e iniciar sesión en Odoo (si no, el robot pedirá usuario y clave).
4. Probar con `carpeta_prueba/`.

## Ejecución en la calificación

1. Pulsar **Ejecutar** en Studio.
2. Elegir la carpeta raíz que entregó el auxiliar.
3. El robot muestra en el **Panel de salida** cada archivo y hoja procesados, abre Chrome,
   importa clientes y luego productos (se ve el clic en *Subir archivo*, la ruta escrita en la
   ventana *Abrir*, *Probar* e *Importar*).
4. Al final aparece un resumen. Los consolidados y `reporte_robot.xlsx` quedan en
   `Documentos\QuetzalMart_RPA\<fecha>\`.
5. Comprobar en Odoo:
   * Contactos ► Filtros ► **Cargados por el RPA**.
   * Inventario ► Productos ► Filtros ► **Cargados por el RPA** (y en la tienda `/shop` los publicados).
   * SQL: sección 9 de `sql/consultas_calificacion.sql`.

## Decisiones de diseño (para explicar en la calificación)

* **Hoja en la 5.ª posición.** El enunciado dice que *clientes* y *productos* siempre vienen en la
  5.ª hoja. El robot revisa primero esa posición; si el libro no la tiene (por ejemplo, los archivos
  de ejemplo del auxiliar, que tienen una sola hoja) busca la hoja por nombre sin distinguir
  mayúsculas, tildes ni espacios. Ambos casos quedan en el reporte con su posición.
* **Sin depender de Excel.** Los nombres de las hojas se leen del propio archivo `.xlsx` (es un ZIP
  con `xl/workbook.xml`), en el orden de las pestañas, aunque el libro esté abierto por otra persona.
* **Columnas en inglés o español.** `Name*`, `Nombre`, `Tax ID`, `NIT`, `Está publicado`,
  `Cantidad a la mano`, etc. se reconocen y se convierten al nombre técnico del campo de Odoo, así
  el asistente de importación relaciona todas las columnas solo y no hay que elegirlas a mano.
* **Valores normalizados.** `Company`/`Compañía` → empresa; `Goods`/`Service` → tipo de producto;
  `True`/`Sí`/`1` → publicado; códigos de barras que Excel guarda como `54398267125.00001` →
  `54398267125`; precios como `Q 32.90` o `21,40` → número.
* **Campos puente (módulo `qm_puente_rpa`).** País, estado, empresa relacionada, etiquetas y sitio
  web viajan como texto y Odoo los convierte en relaciones al guardar; *Cantidad a la mano* registra
  un ajuste de inventario. Así un país escrito como `DE`, `Germany` o `Alemania` no detiene la
  importación de todo el archivo.
* **Sin duplicados.** Cada fila lleva un identificador externo (`ID Externo` del Excel o
  `rpa_cliente_<referencia>`): si el robot se ejecuta dos veces, Odoo actualiza en vez de duplicar,
  y si el mismo cliente viene en dos archivos se carga una vez.
* **Trazabilidad.** Cada contacto y producto guarda en *Archivo de origen (RPA)* la ruta del Excel
  de donde salió (visible en Odoo y en SQL).
* **Robustez.** Si un archivo está dañado, el robot lo anota en el reporte y sigue con el siguiente.
  Después de Probar busca "Todo parece correcto"; si no logra leerlo, lo anota como aviso y
  sigue con Importar (si el archivo tuviera errores, Odoo no importa nada y los muestra).

## Si un selector no funciona

Los selectores se probaron contra Odoo 18 en español con un navegador automatizado:

| Paso | Selector |
|---|---|
| Subir archivo de datos | `<webctrl css-selector='button.o_import_file' tag='BUTTON' />` |
| Ventana *Abrir* de Windows | `<wnd app='chrome.exe' cls='#32770' /><wnd ctrlid='1148' />` |
| Probar | `<webctrl tag='BUTTON' aaname='Probar' />` |
| Resultado correcto | `<webctrl aaname='Todo parece correcto*' />` (tras esperar 6 s) |
| Importar | `<webctrl tag='BUTTON' aaname='Importar' class='btn btn-primary' />` |
| Inicio de sesión | `<webctrl tag='INPUT' name='login' />` y `name='password'` |

Si en su PC alguno no se encuentra (otro idioma de Windows u Odoo, Edge en lugar de Chrome),
haga clic en la actividad ► **Indicar en pantalla** sobre el elemento real y guarde. Si usa Edge,
cambie `BrowserType` de *Abrir navegador* a `Edge` y en el selector de la ventana use `msedge.exe`.

## Resultado esperado

Con `carpeta_prueba/`: 10 Excel encontrados, 7 hojas útiles (6 en la 5.ª
posición y 1 libro de una sola hoja), 6 clientes y 5 productos consolidados, 1 fila vacía y
1 cliente duplicado omitidos. Con los archivos de ejemplo del auxiliar: 4 clientes y 7 productos.

## Ventajas de implementar el RPA

* **Tiempo:** cargar a mano decenas de archivos repartidos en carpetas toma horas; el robot lo
  hace en minutos y sin pasos olvidados.
* **Calidad de datos:** siempre aplica las mismas reglas (formatos, duplicados, tipos), así la base
  centralizada queda consistente aunque cada área nombre distinto sus columnas.
* **Trazabilidad y control:** cada registro sabe de qué archivo vino y cada ejecución deja un reporte.
* **Escalabilidad:** al abrir nuevas sucursales solo crecen las carpetas; el proceso es el mismo.
* **Personas en tareas de valor:** el personal de ventas deja de copiar datos y se dedica a vender
  y atender clientes.
