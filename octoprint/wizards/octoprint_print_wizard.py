from odoo import api, fields, models


class OctoPrintPrintWizard(models.TransientModel):
    _name = 'octoprint.print.wizard'
    _description = 'OctoPrint Wizard'

    print_ids = fields.Many2many('octoprint.print', string='Prints')

    def print(self):
        self.ensure_one()

        for print in self.print_ids:
            pass

        return {'type': 'ir.actions.act_window_close'}
