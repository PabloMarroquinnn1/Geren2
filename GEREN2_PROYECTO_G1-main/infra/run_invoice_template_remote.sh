#!/bin/sh
set -eu

script_name="$1"
case "$script_name" in
  inspect_invoice_template.py|fix_invoice_email_template.py|inspect_email_design.py|apply_email_design.py|test_email_design.py|inspect_design_order.py) ;;
  *) echo 'Unsupported script' >&2; exit 2 ;;
esac

db_password="$(sudo docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' quetzalmart-db | sed -n 's/^POSTGRES_PASSWORD=//p')"
sudo docker cp "/tmp/$script_name" "quetzalmart-odoo:/tmp/$script_name"
if [ "$script_name" = apply_email_design.py ]; then
  sudo docker cp /tmp/qm-email-design quetzalmart-odoo:/tmp/qm-email-design
fi
sudo docker exec -i -e DB_PASSWORD="$db_password" quetzalmart-odoo \
  sh -lc 'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD"' \
  < "/tmp/$script_name"
