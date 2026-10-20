#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Este script debe ejecutarse con sudo." >&2
  exit 1
fi

APP_DIR=/opt/quetzalmart
SOURCE_DIR=/tmp/quetzalmart-block4

cd "${APP_DIR}"
docker compose stop odoo

restore_odoo() {
  cd "${APP_DIR}"
  docker compose up -d odoo >/dev/null 2>&1 || true
}
trap restore_odoo EXIT

docker compose run --rm odoo odoo -d quetzalmart -i payment_demo \
  --load-language=es_419 --stop-after-init --without-demo=all

docker compose run --rm -T odoo odoo shell -d quetzalmart \
  < "${SOURCE_DIR}/seed_block4.py"

trap - EXIT
docker compose up -d odoo

for attempt in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    break
  fi
  if [[ ${attempt} -eq 60 ]]; then
    docker compose logs --tail=100 odoo >&2
    echo "Odoo no estuvo listo después de cargar los datos maestros." >&2
    exit 1
  fi
  sleep 2
done

docker compose ps

