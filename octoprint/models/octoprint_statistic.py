from odoo import api, models, fields


class OctoPrintStatistic(models.Model):
    _name = 'octoprint.statistic'
    _description = 'OctoPrint Statistic'

    name = fields.Char(required=True)

    actual_temperature = fields.Float()
    target_temperature = fields.Float()
    temperature_offset = fields.Float()

    filament_length = fields.Float()
    filament_volume = fields.Float()

    print_id = fields.Many2one('octoprint.print')
