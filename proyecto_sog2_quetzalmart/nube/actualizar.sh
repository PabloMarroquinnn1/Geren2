#!/usr/bin/env bash
# Aplica cambios de los módulos propios después de un "git pull".
# Uso: sudo ./actualizar.sh [modulo1,modulo2]   (por defecto todos los qm_*)
set -Eeuo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source .env
set +a

modulos=${1:-qm_implementacion,qm_puente_rpa,qm_ga4_ecommerce,qm_crm_postventa,qm_gestion_documental}
docker compose stop odoo
docker compose run --rm odoo odoo -d "${BD_NOMBRE}" -u "${modulos}" --stop-after-init
docker compose up -d
echo "Módulos actualizados: ${modulos}"
