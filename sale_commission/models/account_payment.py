from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    commission_ids = fields.One2many('sale.commission', 'payment_id')
    commission_count = fields.Integer(compute='_compute_commission_count')

    @api.depends('commission_ids')
    def _compute_commission_count(self):
        for record in self:
            record.commission_count = len(record.commission_ids)

    def action_view_commissions(self):
        self.ensure_one()
        return {
            'name': 'Sales Commissions',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.commission',
            'domain': [('payment_id', '=', self.id)],
        }

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        for record in self:
            for commission in record.commission_ids:
                commission.state = 'open'
                commission._compute_state()
        return res

    def action_cancel(self):
        res = super(AccountPayment, self).action_cancel()
        for record in self:
            for commission in record.commission_ids:
                commission.state = 'cancel'
        return res
