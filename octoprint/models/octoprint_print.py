from odoo import api, models, fields
from odoo.exceptions import UserError


class OctoPrintPrint(models.Model):
    _name = 'octoprint.print'
    _description = 'OctoPrint Print'

    name = fields.Char(default='New', required=True, copy=False, readonly=True)
    mrp_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    stl_file = fields.Binary(string='STL File')
    stl_file_name = fields.Char(string='STL File Name')
    slicer_id = fields.Many2one('octoprint.slicer')
    printer_id = fields.Many2one(related='slicer_id.printer_id')
    state = fields.Selection(
        [
            ('open', 'Open'),
            ('print', 'Printing'),
            ('done', 'Finished'),
            ('error', 'Error'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='open',
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('octoprint.print')
        return super(OctoPrintPrint, self).create(vals_list)

    def _compute_state(self):
        # TODO: API call using GET /api/job
        # Returns only the currently printing job

        for record in self:
            record.state = 'open'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_print(self):
        if len(self) != 1:
            raise UserError('Please select exactly one record to print.')
        if self.state != 'open':
            raise UserError('Please select an open record to print.')
        domain = [('state', '=', 'printing'), ('printer_id', '=', self.printer_id.id)]
        if len(self.env['octoprint.print'].search(domain)) > 0:
            raise UserError('Please wait for the current print to finish.')
