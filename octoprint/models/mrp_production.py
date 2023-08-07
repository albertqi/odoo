from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    stl_file = fields.Binary(string='STL File')
    stl_file_name = fields.Char(string='STL File Name')
    slicer_id = fields.Many2one('octoprint.slicer')
    printer_id = fields.Many2one('octoprint.printer')
    print_ids = fields.One2many('octoprint.print', 'mrp_id', string='Prints')
    print_count = fields.Integer(compute='_compute_print_count')

    @api.depends('print_ids')
    def _compute_print_count(self):
        for record in self:
            record.print_count = len(record.print_ids)

    def action_view_prints(self):
        self.ensure_one()
        return {
            'name': 'Prints',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'octoprint.print',
            'domain': [('mrp_id', '=', self.id)],
        }
