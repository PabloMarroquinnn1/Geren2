# QuetzalMart — Proyecto GEREN2

Repositorio de trabajo para la implementación del proyecto en Odoo Community, UiPath y Google Cloud.

## Estructura

- `datos/`: archivos de carga y datos de prueba separados por proceso.
- `rpa/`: proyecto de UiPath.
- `consultas_sql/`: consultas para la validación en PostgreSQL durante la evaluación.
- `capturas/`: evidencias organizadas para los tres manuales.
- `manual_1/`, `manual_2/`, `manual_3/`: documentos finales.
- `BLOQUE_7_GOOGLE_ANALYTICS.md`: configuración y evidencia del bloque de GA4.
- `BLOQUE_8_RPA.md`: flujo, restricciones y evidencia del robot de UiPath.
- `outputs/`: entregables generados por Codex.
- `tmp/`: archivos temporales de construcción y verificación.

## Reglas importantes del proyecto

- Odoo debe usar una única base de datos PostgreSQL en la nube.
- La carga de clientes y productos con UiPath debe hacerse mediante la interfaz de Odoo; no se utilizará API de Odoo desde UiPath.
- Las hojas de carga deben conservar exactamente los nombres exigidos por el enunciado: `clientes` y `productos`.
- Las evidencias se tomarán durante la implementación y se asociarán al manual correspondiente.
