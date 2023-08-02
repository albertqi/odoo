from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleCommissionType(models.Model):
    _name = 'sale.commission.type'
    _description = 'Sales Commission Type'

    name = fields.Char(required=True)
    type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed')],
        required=True,
    )
    rate = fields.Float(required=True)
    due = fields.Selection(
        [('per_payment', 'Per Payment'), ('settled', 'Settled')],
        required=True,
    )

    @api.constrains('rate', 'type')
    def _check_rate(self):
        for record in self:
            if record.rate < 0:
                raise ValidationError('Rate cannot be negative.')
            if record.type == 'percentage' and record.rate > 1:
                raise ValidationError('Rate must be between 0 and 1.')
