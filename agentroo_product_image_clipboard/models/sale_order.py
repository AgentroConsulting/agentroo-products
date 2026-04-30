# -*- coding: utf-8 -*-
# Part of Agentroo Consultings.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_image_128 = fields.Image(
        string="Image",
        related="product_id.image_128",
        max_width=128,
        max_height=128,
        readonly=True,
    )
