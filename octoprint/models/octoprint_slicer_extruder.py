from odoo import api, models, fields

class OctoPrintSlicerExtruder(models.Model):
    _name='octoprint.slicer.extruder'
    
    slicer_id = fields.Many2one('octoprint.slicer', required=True)
    extruder_temperture = fields.Integer(default=210, required=True)
    extruder_filament_diameter = fields.Float(required=True)