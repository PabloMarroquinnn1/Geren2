#!/usr/bin/env bash
set -euo pipefail

sudo docker cp /tmp/install_website_crm_module.py quetzalmart-odoo:/tmp/install_website_crm_module.py
sudo docker cp /tmp/sync_existing_website_orders_to_crm.py quetzalmart-odoo:/tmp/sync_existing_website_orders_to_crm.py

DB_PASSWORD="$(sudo awk -F= '/^POSTGRES_PASSWORD=/{print substr($0,index($0,"=")+1)}' /opt/quetzalmart/.env)"

sudo docker exec -i -e DB_PASSWORD="$DB_PASSWORD" quetzalmart-odoo sh -lc \
  'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD" < /tmp/install_website_crm_module.py'

sudo docker exec -i -e DB_PASSWORD="$DB_PASSWORD" quetzalmart-odoo sh -lc \
  'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD" < /tmp/sync_existing_website_orders_to_crm.py'

sudo docker restart quetzalmart-odoo >/dev/null
sudo docker inspect -f '{{.State.Status}}' quetzalmart-odoo
