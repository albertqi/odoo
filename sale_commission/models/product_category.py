from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    commission_type = fields.Many2one('sale.commission.type')
