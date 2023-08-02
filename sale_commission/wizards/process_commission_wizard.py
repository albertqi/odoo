from odoo import api, fields, models
from odoo import Command
from odoo.exceptions import ValidationError


class ProcessCommissionWizard(models.TransientModel):
    _name = 'process.commission.wizard'
    _description = 'Process Commission Wizard'

    commission_ids = fields.Many2many(
        'sale.commission',
        string='Settlements',
    )

    @api.onchange('commission_ids')
    def _onchange_commission_ids(self):
        for record in self:
            if record.commission_ids and record.commission_ids.filtered(
                lambda r: r.state != 'open'
            ):
                raise ValidationError('Only open settlements can be processed.')

    def _create_vendor_bill(self, partner_id, commissions):
        self.ensure_one()

        # Create invoice line for commission.
        def create_invoice_line(commission):
            return {
                'name': f'Commission Payout ({commission.name})',
                'price_unit': commission.commission_amount,
            }

        # Create invoice for commission.
        record = {
            'partner_id': partner_id.id,
            'move_type': 'in_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                Command.create(create_invoice_line(commission))
                for commission in commissions
            ],
        }

        return self.env['account.move'].create(record).id

    def process_commission(self):
        self.ensure_one()

        # Calculate commissions for each partner.
        commissions_record = {}
        for commission in self.commission_ids:
            partner_id = commission.partner_id
            if commissions_record.get(partner_id):
                commissions_record[partner_id].append(commission)
            else:
                commissions_record[partner_id] = [commission]

        for partner_id, commissions in commissions_record.items():
            vendor_bill_id = self._create_vendor_bill(partner_id, commissions)
            for commission in commissions:
                record = {
                    'vendor_bill_id': vendor_bill_id,
                    'state': 'bill',
                }
                commission.write(record)

        return {'type': 'ir.actions.act_window_close'}
