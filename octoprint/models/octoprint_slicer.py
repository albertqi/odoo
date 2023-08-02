from odoo import api, models, fields


class OctoPrintSlicer(models.Model):
    _name = 'octoprint.slicer'
    _description = 'OctoPrint Slicer'

    name = fields.Char(string='Name', required=True)
    printer_id = fields.Many2one('octoprint.printer')

    # Slicer Data TODO
    color = fields.Char(string='Color')
    model = fields.Char(string='Model', required=True)
    default = fields.Boolean(string='Default')
    current = fields.Boolean(string='Current')
