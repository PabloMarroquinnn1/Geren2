"""Hace visible la barra de consentimiento para que GA4 pueda cargar con consentimiento."""

env = env  # noqa: F821 - proporcionado por odoo shell
view = env["ir.ui.view"].browse(1414).exists()
if not view:
    raise RuntimeError("No se encontró la vista website.cookies_bar (id 1414)")

for lang in ("en_US", "es_GT", "es_419"):
    localized = view.with_context(lang=lang)
    arch = localized.arch_db
    arch = arch.replace(
        'class="s_popup o_snippet_invisible d-none o_no_save"',
        'class="s_popup o_no_save"',
    )
    arch = arch.replace(' data-invisible="1"', "")
    localized.write({"arch": arch})

env.cr.commit()
print({"cookie_bar_view": view.id, "enabled_languages": ["en_US", "es_GT", "es_419"]})
