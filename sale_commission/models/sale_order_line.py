from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commission_partner_id = fields.Many2one('res.partner')
    commission_type = fields.Many2one(
        'sale.commission.type',
        compute='_compute_commission_type',
        readonly=False,
        store=True,
    )
    commission_forecast = fields.Monetary(compute='_compute_commission_forecast')

    @api.depends('product_id')
    def _compute_commission_type(self):
        for record in self:
            record.commission_type = record.product_id.categ_id.commission_type

    @api.depends('price_subtotal', 'commission_type')
    def _compute_commission_forecast(self):
        for record in self:
            record.commission_forecast = (
                record.price_subtotal * record.commission_type.rate
                if record.commission_type.type == 'percentage'
                else record.commission_type.rate
            )

    @api.constrains('commission_partner_id', 'commission_type')
    def _check_commission_information(self):
        for record in self:
            if (not record.commission_partner_id) != (not record.commission_type):
                raise ValidationError(
                    'Commission partner and type must either both be present or both be empty.'
                )

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        commission_record = {
            'commission_partner_id': self.commission_partner_id.id,
            'commission_type': self.commission_type.id,
            'commission_forecast': self.commission_forecast,
        }
        res.update(commission_record)
        return res
