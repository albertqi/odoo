from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    stl_file = fields.Binary(string='STL File')

    def action_start_octoprint_job(self):
        return
