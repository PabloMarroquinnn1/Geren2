#!/bin/sh
set -eu

db_password="$(sudo docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' quetzalmart-db | sed -n 's/^POSTGRES_PASSWORD=//p')"
sudo docker cp /tmp/seed_block7_product_images.py quetzalmart-odoo:/tmp/seed_block7_product_images.py
sudo docker cp /tmp/seed_product_images_wrapper.py quetzalmart-odoo:/tmp/seed_product_images_wrapper.py
sudo docker exec -i -e DB_PASSWORD="$db_password" quetzalmart-odoo \
  sh -lc 'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD"' \
  < /tmp/seed_product_images_wrapper.py
sudo docker restart quetzalmart-odoo
