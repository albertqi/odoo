from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

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

    def _create_sale_commission(self, line, account_move_id, account_payment_id):
        if not line.commission_partner_id:
            return

        # What percent of the invoice was just paid.
        percent_paid = account_payment_id.amount / account_move_id.amount_total

        commission_amount = 0
        if line.commission_type.due == 'settled':
            if account_move_id.payment_state == 'paid':
                commission_amount = line.commission_forecast
            else:
                return
        elif line.commission_type.due == 'per_payment':
            commission_amount = line.commission_forecast * percent_paid

        record = {
            'partner_id': line.commission_partner_id.id,
            'commission_amount': commission_amount,
            'payment_id': account_payment_id.id,
            'payment_amount': account_payment_id.amount,
            'account_move_id': account_move_id.id,
        }
        self.env['sale.commission'].create(record)

    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()

        account_move_id = account_payment_id = None
        for line in self:
            if line.display_type == 'payment_term':
                account_move_id = line.move_id
            elif line.display_type == 'product':
                account_payment_id = line.payment_id

        if not account_move_id or not account_payment_id:
            return res

        match account_move_id.move_type:
            case 'out_invoice':
                for line in account_move_id.invoice_line_ids.filtered(
                    lambda r: r.commission_partner_id
                ):
                    self._create_sale_commission(
                        line, account_move_id, account_payment_id
                    )
            case 'in_invoice':
                if account_move_id.payment_state == 'paid':
                    for commission in account_move_id.bill_commission_ids:
                        commission.state = 'paid'
            case _:
                return res

        return res
