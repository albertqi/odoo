from odoo import api, fields, models


SALE_COMMISSION_VIEW = {
    'name': 'Sales Commissions',
    'type': 'ir.actions.act_window',
    'view_mode': 'tree,form',
    'res_model': 'sale.commission',
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_commission_ids = fields.One2many('sale.commission', 'account_move_id')
    bill_commission_ids = fields.One2many('sale.commission', 'vendor_bill_id')

    invoice_commission_count = fields.Integer(
        compute='_compute_invoice_commission_count'
    )
    bill_commission_count = fields.Integer(compute='_compute_bill_commission_count')

    @api.depends('invoice_commission_ids')
    def _compute_invoice_commission_count(self):
        for record in self:
            record.invoice_commission_count = len(record.invoice_commission_ids)

    @api.depends('bill_commission_ids')
    def _compute_bill_commission_count(self):
        for record in self:
            record.bill_commission_count = len(record.bill_commission_ids)

    def action_view_invoice_commissions(self):
        self.ensure_one()
        return SALE_COMMISSION_VIEW | {'domain': [('account_move_id', '=', self.id)]}

    def action_view_bill_commissions(self):
        self.ensure_one()
        return SALE_COMMISSION_VIEW | {'domain': [('vendor_bill_id', '=', self.id)]}

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for record in self:
            if record.move_type == 'out_invoice':
                for commission in record.invoice_commission_ids:
                    commission.state = 'cancel'
            elif record.move_type == 'in_invoice':
                for commission in record.bill_commission_ids:
                    commission.state = 'bill'
        return res

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for record in self:
            for commission in record.invoice_commission_ids:
                commission.state = 'cancel'
            for commission in record.bill_commission_ids:
                commission.state = 'cancel'
        return res
