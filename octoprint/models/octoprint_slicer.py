from odoo import api, models, fields

class OctoprintSlicer(models.Model):
    _name = "octoprint.slicer"
    _description = "Octoprint Slicer"
    
    # Profile stuff
    name = fields.Char(string="Name", required=True)
    color = fields.Char(string="Color")
    model = fields.Char(string="Model", required=True)
    default = fields.Boolean(string="Default")
    current = fields.Boolean(string="Current")
    