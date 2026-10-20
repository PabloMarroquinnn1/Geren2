#!/usr/bin/env bash
# Copia de seguridad de la base y de los archivos adjuntos de Odoo.
# Uso: sudo ./respaldo.sh     -> respaldos/AAAAMMDD-HHMM/
set -Eeuo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source .env
set +a

destino="respaldos/$(date +%Y%m%d-%H%M)"
mkdir -p "${destino}"
docker compose exec -T db pg_dump -U odoo -Fc "${BD_NOMBRE}" > "${destino}/${BD_NOMBRE}.dump"
docker compose exec -T odoo tar -C /var/lib/odoo -czf - filestore/"${BD_NOMBRE}" > "${destino}/filestore.tar.gz"
ls -lh "${destino}"
