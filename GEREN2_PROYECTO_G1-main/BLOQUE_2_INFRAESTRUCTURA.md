# Bloque 2 — Infraestructura de Google Cloud

## Objetivo

Crear el entorno en la nube donde se alojarán Odoo Community y PostgreSQL centralizados.

## Resultado

La infraestructura quedó creada y verificada:

| Recurso | Configuración |
|---|---|
| Proyecto GCP | `quetzalmart-geren2-2026` |
| VM | `quetzalmart-odoo` |
| Zona | `us-central1-a` |
| Sistema operativo | Ubuntu 24.04 LTS |
| Máquina | `e2-standard-2` |
| Disco | 30 GB `pd-balanced` |
| IP estática | `34.9.149.41` |
| Puertos web | TCP 80 y 443 |
| Acceso administrativo | SSH verificado con Google Cloud CLI |

## Decisiones

Se utilizará una sola VM para la demostración académica. En ella se instalarán Odoo Community y PostgreSQL, manteniendo la base de datos centralizada como indicó el auxiliar. La IP estática evitará que el enlace de acceso cambie entre sesiones.

## Pendiente para el bloque 3

Instalar Docker, levantar PostgreSQL y Odoo Community, configurar el acceso web y crear la base de datos del proyecto.

