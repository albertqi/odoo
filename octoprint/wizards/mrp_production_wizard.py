from odoo import api, fields, models


class MrpProductionWizard(models.TransientModel):
    _name = 'mrp.production.wizard'
    _description = 'Manufacturing Wizard'

    mrp_ids = fields.Many2many('mrp.production', string='Manufacturing Orders')

    def create_prints(self):
        self.ensure_one()

        for mrp in self.mrp_ids:
            record = {
                'mrp_id': mrp.id,
                'stl_file': mrp.stl_file,
                'stl_file_name': mrp.stl_file_name,
                'slicer_id': mrp.slicer_id.id,
            }
            self.env['octoprint.print'].create(record)

        return {'type': 'ir.actions.act_window_close'}
