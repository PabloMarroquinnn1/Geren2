#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Este script debe ejecutarse con sudo." >&2
  exit 1
fi

cd /opt/quetzalmart
docker compose stop odoo
trap 'docker compose up -d odoo >/dev/null 2>&1 || true' EXIT

docker compose run --rm odoo odoo -d quetzalmart \
  -i delivery \
  --stop-after-init --without-demo=all

trap - EXIT
docker compose up -d odoo
