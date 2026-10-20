from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # La columna "Cantidad a la mano" del Excel no puede importarse en el campo
    # estándar qty_available (es calculado). El robot la envía a este campo y Odoo
    # registra el ajuste de inventario correspondiente.
    qm_cantidad_inicial = fields.Float(
        string="Cantidad a la mano (carga RPA)",
        digits="Product Unit of Measure",
        copy=False,
        help="Cantidad indicada en el archivo de Excel. Al guardarla se aplica un "
             "ajuste de inventario en la ubicación de carga del RPA.",
    )
    qm_valores_producto = fields.Text(string="Valores del producto", copy=False)
    qm_origen_rpa = fields.Char(
        string="Archivo de origen (RPA)",
        copy=False,
        help="Ruta del Excel desde el que el robot cargó este producto.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        productos = super().create(vals_list)
        productos.filtered("qm_cantidad_inicial")._qm_aplicar_cantidad_inicial()
        return productos

    def write(self, vals):
        resultado = super().write(vals)
        if vals.get("qm_cantidad_inicial"):
            self._qm_aplicar_cantidad_inicial()
        return resultado

    @api.model
    def _qm_ubicacion_carga(self):
        parametro = self.env["ir.config_parameter"].sudo().get_param("qm_puente_rpa.ubicacion_id")
        ubicacion = self.env["stock.location"].browse(int(parametro or 0)).exists()
        if not ubicacion:
            almacen = self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], order="sequence, id", limit=1
            )
            ubicacion = almacen.lot_stock_id
        return ubicacion

    def _qm_aplicar_cantidad_inicial(self):
        ubicacion = self._qm_ubicacion_carga()
        Quant = self.env["stock.quant"].sudo().with_context(
            inventory_mode=True,
            set_inventory_quantity_auto_apply=True,
            inventory_name="Carga inicial RPA",
        )
        for plantilla in self:
            # Servicios y combos no manejan existencias: se ignora la cantidad.
            if plantilla.type != "consu" or not ubicacion:
                continue
            if not plantilla.is_storable:
                plantilla.is_storable = True
            for variante in plantilla.product_variant_ids:
                quant = Quant.search([
                    ("product_id", "=", variante.id),
                    ("location_id", "=", ubicacion.id),
                    ("lot_id", "=", False),
                    ("package_id", "=", False),
                ], limit=1)
                if not quant:
                    quant = Quant.create({"product_id": variante.id, "location_id": ubicacion.id})
                quant.inventory_quantity = plantilla.qm_cantidad_inicial
                quant.action_apply_inventory()
