from odoo import api, models, fields

class OctoprintPrinter(models.Model):
    _name = "octoprint.printer"
    _description = "Octoprint Printer"
    
    # Printer Stuff
    name = fields.Char(string="Printer name", required=True)
    printer_id = fields.Integer(string="Printer ID", required=True)
    color = fields.Char(string="Color", default="default")
    model = fields.Char(string="Model", required=True)
    default = fields.Boolean(string="Default")
    current = fields.Boolean(string="Current")
    has_heated_bed = fields.Boolean(string="Has Heated Bed")
    has_heated_chamber = fields.Boolean(string="Has Heated Chamber")
    
    # Print volume
    volume_form_factor = fields.Selection([
        ('rectangular', "rectangular"),
        ('circular', "circular"),
    ])
    volume_origin = fields.Selection([
        ('lowerleft', "lowerleft"),
        ('center', "center"),
    ])
    volume_width = fields.Float(string="Width")
    volume_depth = fields.Float(string="Depth")
    volume_height = fields.Float(string="Height")
    volume_custom_box = fields.Boolean(string="Custom box")

    volume_custom_box_min_x = fields.Float(string="Min X")
    volume_custom_box_min_y = fields.Float(string="Min Y")
    volume_custom_box_min_z = fields.Float(string="Min Z")

    volume_custom_box_max_x = fields.Float(string="Max X")
    volume_custom_box_max_y = fields.Float(string="Max Y")
    volume_custom_box_max_z = fields.Float(string="Max Z")

    # Axes
    axes_x_speed = fields.Char(string="X axis speed")
    axes_y_speed = fields.Char(string="Y axis speed")
    axes_z_speed = fields.Char(string="Z axis speed")
    axes_e_speed = fields.Char(string="E axis speed")

    axes_x_inverted = fields.Boolean(string="X axis inverted")
    axes_y_inverted = fields.Boolean(string="Y axis inverted")
    axes_z_inverted = fields.Boolean(string="Z axis inverted")
    axes_e_inverted = fields.Boolean(string="E axis inverted")

    # Extruder
    extruder_count = fields.Integer(string="Extruder count")
    extruder_shared_nozzle = fields.Boolean(string="Shared nozzle", default=False)
    extruder_nozzle_diameter = fields.Float(string="Nozzle diameter")
    extruder_nozzle_extrusion_length = fields.Float(string="Default extrusion length")