from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleCommission(models.Model):
    _name = 'sale.commission'
    _description = 'Sales Commission'

    name = fields.Char(default='New', required=True, copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', required=True)
    currency_id = fields.Many2one(
        'res.currency', related='partner_id.currency_id', required=True
    )
    commission_amount = fields.Monetary(required=True)
    payment_id = fields.Many2one('account.payment', readonly=True)
    payment_amount = fields.Monetary(
        related='payment_id.amount', string='Payment Amount'
    )
    account_move_id = fields.Many2one(
        'account.move',
        string='Invoice',
        domain=[('move_type', '=', 'out_invoice')],
        readonly=True,
    )
    state = fields.Selection(
        [
            ('open', 'Open'),
            ('bill', 'Bill Created'),
            ('paid', 'Bill Paid'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='open',
        required=True,
    )
    vendor_bill_id = fields.Many2one(
        'account.move', domain=[('move_type', '=', 'in_invoice')], readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('name')
        return super(SaleCommission, self).create(vals_list)

    @api.ondelete(at_uninstall=False)
    def _unlink_if_cancel(self):
        for record in self:
            if record.state != 'cancel':
                raise UserError("You can only delete a cancelled sales commission.")

    @api.constrains('commission_amount')
    def _check_commission_amount(self):
        for record in self:
            if record.commission_amount < 0:
                raise ValidationError('Commission amount cannot be negative.')

    def _compute_state(self):
        for record in self:
            if record.state == 'cancel':
                continue
            if not record.vendor_bill_id:
                record.state = 'open'
            elif record.vendor_bill_id.payment_state != 'paid':
                record.state = 'bill'
            else:
                record.state = 'paid'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_open(self):
        for record in self:
            record.state = 'open'
            self._compute_state()
