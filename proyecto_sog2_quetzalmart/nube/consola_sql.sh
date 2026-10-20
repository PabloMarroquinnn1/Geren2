#!/usr/bin/env bash
# Abre psql dentro de la VM con el usuario de solo lectura.
# Uso: sudo ./consola_sql.sh                 (interactivo)
#      sudo ./consola_sql.sh < ../sql/consultas_calificacion.sql
set -Eeuo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source .env
set +a
exec docker compose exec -e PGPASSWORD="${CONSULTA_PASSWORD}" db \
  psql -h 127.0.0.1 -U consulta -d "${BD_NOMBRE}" "$@"
