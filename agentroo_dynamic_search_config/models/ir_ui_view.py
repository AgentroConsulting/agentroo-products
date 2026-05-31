from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _dynamic_search_clear_caches(self):
        self.env.registry.clear_cache()
