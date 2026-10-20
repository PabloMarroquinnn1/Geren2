# Bloque 8 — RPA con UiPath

## Objetivo

Crear un robot que recorra una carpeta con subcarpetas, encuentre archivos .xlsx, detecte únicamente las hojas con nombre exacto clientes y productos, y cargue la información en Odoo utilizando la interfaz web de importación.

El robot no usa API de Odoo, llamadas HTTP ni inserciones directas en PostgreSQL. La carga se realiza con actividades de Excel para leer y preparar los datos y actividades de UI Automation para interactuar con el navegador y Odoo.

## Flujo implementado

1. Solicita la carpeta raíz que entregará el auxiliar durante la evaluación.
2. Busca archivos .xlsx en toda la jerarquía mediante SearchOption.AllDirectories.
3. Abre cada Excel y obtiene los nombres de sus hojas.
4. Procesa clientes solamente si existe con ese nombre exacto.
5. Procesa productos solamente si existe con ese nombre exacto.
6. Lee cada hoja con encabezados y crea un archivo temporal de una sola hoja para evitar ambigüedad en el asistente de importación.
7. Abre la lista correspondiente en Odoo.
8. Selecciona Importar, carga el archivo temporal y confirma la importación.
9. Registra el progreso en el panel de salida y muestra un aviso al finalizar.

## Archivo principal

El flujo está en:

rpa/QuetzalMart_RPA/Main.xaml

Los nombres de las actividades comienzan con TODO Indicar en los cuatro puntos que necesitan capturar el selector real del navegador:

- botón Importar de clientes;
- selector de archivo de clientes;
- botón Importar de productos;
- selector de archivo de productos.

Los selectores web quedaron restringidos a la página administrativa de Odoo (`title='Odoo'`) para evitar que UiPath tome por error la pestaña de Conversaciones u otra página de Chrome. La vista real fue verificada en Odoo: Lista → Acciones → Importar registros → Subir archivo de datos. Si el auxiliar utiliza otro navegador, idioma o versión, se debe usar **Indicar elemento en pantalla** sobre cada actividad marcada como TODO Indicar y guardar el proyecto.

## Preparación para la prueba

1. Abrir rpa/QuetzalMart_RPA en UiPath Studio.
2. Verificar que estén instalados UiPath.Excel.Activities, UiPath.System.Activities y UiPath.UIAutomation.Activities.
3. Iniciar sesión en Odoo antes de ejecutar el robot.
4. Ejecutar el flujo con una carpeta de prueba que contenga un Excel con hojas exactamente clientes y productos.
5. Indicar los elementos marcados como TODO Indicar si UiPath solicita recapturar los selectores; la indicación debe hacerse sobre la ventana administrativa de Odoo, no sobre Conversaciones ni sobre otra pestaña.
6. Revisar el panel de salida y confirmar los registros desde Odoo.
7. Repetir con la carpeta jerárquica entregada por el auxiliar.

## Evidencia que debe guardarse

- Proyecto abierto en UiPath Studio.
- Actividad que solicita la carpeta raíz.
- Actividad de recorrido recursivo.
- Detección de hojas exactas.
- Lectura y preparación de clientes.
- Lectura y preparación de productos.
- Importación en Odoo.
- Panel de salida sin errores.
- Registro visible en Odoo y consulta SQL correspondiente.

## Estado

La base del flujo y su documentación ya están creadas. La captura final de selectores y la ejecución de prueba quedan como validación en UiPath Studio, porque son elementos dependientes de la sesión gráfica del navegador.
