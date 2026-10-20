#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR=/tmp/quetzalmart-materiales-operativos
ASSET_SOURCE="${SOURCE_DIR}/assets/brand/internal_materials"
CONTAINER=quetzalmart-odoo
CONTAINER_DIR=/tmp/quetzalmart-materiales-operativos

if [[ ! -f "${SOURCE_DIR}/infra/seed_internal_materials.py" ]]; then
  echo "No se encontró el script de carga de materiales." >&2
  exit 2
fi
if [[ ! -f "${SOURCE_DIR}/datos/materiales_operativos_60.json" ]]; then
  echo "No se encontró el manifiesto de 60 materiales." >&2
  exit 2
fi
if [[ $(find "${ASSET_SOURCE}" -maxdepth 1 -type f -name 'QMI-*.png' | wc -l) -ne 60 ]]; then
  echo "Se requieren exactamente 60 imágenes PNG QMI." >&2
  exit 2
fi

sudo docker exec "${CONTAINER}" mkdir -p "${CONTAINER_DIR}/assets" "${CONTAINER_DIR}/datos"
sudo docker cp "${ASSET_SOURCE}/." "${CONTAINER}:${CONTAINER_DIR}/assets/"
sudo docker cp "${SOURCE_DIR}/datos/materiales_operativos_60.json" "${CONTAINER}:${CONTAINER_DIR}/datos/materiales_operativos_60.json"

db_password="$(sudo docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' quetzalmart-db | sed -n 's/^POSTGRES_PASSWORD=//p')"
sudo docker exec -i -e DB_PASSWORD="${db_password}" "${CONTAINER}" \
  sh -lc 'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD"' \
  < "${SOURCE_DIR}/infra/seed_internal_materials.py"

