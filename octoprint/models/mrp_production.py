from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    stl_file = fields.Binary(string='STL File')
    stl_file_name = fields.Char(string='STL File Name')
    slicer_id = fields.Many2one('octoprint.slicer')
    printer_id = fields.Many2one(related='slicer_id.printer_id')
    print_ids = fields.One2many('octoprint.print', 'mrp_id', string='Prints')
