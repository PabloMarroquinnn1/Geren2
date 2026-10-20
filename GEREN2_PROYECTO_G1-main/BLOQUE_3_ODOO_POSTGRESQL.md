# Bloque 3 — Odoo Community 18 y PostgreSQL

## Resultado

Odoo Community 18 y PostgreSQL 16 están instalados en la VM `quetzalmart-odoo`. La aplicación está disponible mediante HTTPS en:

`https://quetzalmart.34-9-149-41.sslip.io`

## Arquitectura

| Componente | Implementación |
|---|---|
| Odoo | Contenedor oficial `odoo:18.0` |
| Base de datos | Contenedor `postgres:16-alpine` |
| Base de aplicación | `quetzalmart` |
| Proxy web | Nginx |
| HTTPS | Let's Encrypt con renovación automática |
| Persistencia | Volúmenes Docker para Odoo y PostgreSQL |
| Red de datos | Red Docker privada |

## Seguridad aplicada

- PostgreSQL no publica el puerto 5432 hacia Internet.
- Odoo escucha internamente en `127.0.0.1:8069` y `127.0.0.1:8072`.
- Nginx es el único punto de entrada público por los puertos 80 y 443.
- Las solicitudes HTTP redirigen a HTTPS.
- El listado y la administración pública de bases de datos están desactivados mediante `list_db = False` y `dbfilter = ^quetzalmart$`.
- Las contraseñas se generan aleatoriamente y no se incluyen en los archivos de infraestructura del repositorio.

## Archivos reproducibles

- `infra/docker-compose.yml`: definición de Odoo y PostgreSQL.
- `infra/odoo.conf`: configuración base de Odoo.
- `infra/nginx-quetzalmart.conf`: proxy web.
- `infra/deploy_odoo18.sh`: instalación y despliegue idempotente.

## Verificaciones realizadas

- Contenedor PostgreSQL en estado saludable.
- Contenedor Odoo en ejecución.
- Login web de Odoo devuelve HTTP 200 mediante HTTPS.
- HTTP devuelve redirección 301 hacia HTTPS.
- Puertos 5432 y 8069 cerrados al acceso externo.
- Consulta directa en PostgreSQL confirma la base `quetzalmart`, la compañía `QuetzalMart` y el administrador configurado.

## Credenciales

Las credenciales están almacenadas en `.secrets/odoo_credentials.txt`. Esta carpeta está oculta y excluida mediante `.gitignore`. No debe enviarse con los manuales ni subirse a un repositorio.

