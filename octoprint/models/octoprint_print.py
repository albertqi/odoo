from odoo import api, models, fields


class OctoPrintPrint(models.Model):
    _name = 'octoprint.print'
    _description = 'OctoPrint Print'

    name = fields.Char(required=True)
    mrp_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    stl_file = fields.Binary(string='STL File')
    stl_file_name = fields.Char(string='STL File Name')
    slicer_id = fields.Many2one('octoprint.slicer')
    printer_id = fields.Many2one(related='slicer_id.printer_id')
    state = fields.Char(compute='_compute_state')

    def _compute_state(self):
        # TODO: API call using GET /api/job
        # Returns only the currently printing job

        for record in self:
            record.state = 'Printing'

    def action_start_octoprint_job(self):
        return
