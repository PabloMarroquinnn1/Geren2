"""Install the QuetzalMart website-to-CRM integration; run with Odoo shell."""

env["ir.module.module"].update_list()
module = env["ir.module.module"].search(
    [("name", "=", "quetzalmart_website_crm")],
    limit=1,
)
if not module:
    raise RuntimeError("The quetzalmart_website_crm addon was not discovered")

if module.state == "uninstalled":
    module.button_immediate_install()
elif module.state != "installed":
    raise RuntimeError("Unexpected addon state: %s" % module.state)

env.cr.commit()
print(
    {
        "module": module.name,
        "state": module.state,
    }
)
