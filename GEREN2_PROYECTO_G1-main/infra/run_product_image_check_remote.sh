#!/bin/sh
set -eu

db_password="$(sudo docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' quetzalmart-db | sed -n 's/^POSTGRES_PASSWORD=//p')"
batch_start="${1:-1}"
sudo docker exec -i -e DB_PASSWORD="$db_password" -e BATCH_START="$batch_start" quetzalmart-odoo \
  sh -lc 'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD"' \
  < /tmp/check_product_images.py
