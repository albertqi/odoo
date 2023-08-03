from odoo import api, models, fields


class OctoPrintExtruder(models.Model):
    _name = 'octoprint.extruder'
    _description = 'OctoPrint Extruder'

    x_offset = fields.Float(default=0.0, required=True)
    y_offset = fields.Float(default=0.0, required=True)
    printer_id = fields.Many2one('octoprint.printer')
