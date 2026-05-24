from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_menu_ids = fields.Many2many(
        comodel_name='ir.ui.menu',
        relation='res_users_allowed_menu_rel',
        string='Allowed Apps',
        domain=[('parent_id', '=', False)],
        help="Only these app menus will be visible to this user. "
             "Leave empty to show all apps.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['allowed_menu_ids']

    def write(self, vals):
        res = super().write(vals)
        if 'allowed_menu_ids' in vals:
            # Clear menu cache so visibility changes take effect immediately
            self.env.registry.clear_cache()
        return res
