from odoo import api, models, fields


class OctoPrintPrinter(models.Model):
    _name = 'octoprint.printer'
    _description = 'OctoPrint Printer'

    name = fields.Char(required=True)
    slicer_ids = fields.One2many('octoprint.slicer', 'printer_id', string='Slicers')

    # Printer Data
    printer_id = fields.Integer(string='Printer ID', required=True)
    color = fields.Char(default='default')
    model = fields.Char(required=True)
    default = fields.Boolean()
    current = fields.Boolean()
    has_heated_bed = fields.Boolean()
    has_heated_chamber = fields.Boolean()

    # Print Volume
    volume_form_factor = fields.Selection(
        [
            ('rectangular', 'rectangular'),
            ('circular', 'circular'),
        ]
    )
    volume_origin = fields.Selection(
        [
            ('lowerleft', 'lowerleft'),
            ('center', 'center'),
        ]
    )
    volume_width = fields.Float(string='Width')
    volume_depth = fields.Float(string='Depth')
    volume_height = fields.Float(string='Height')
    volume_custom_box = fields.Boolean(string='Custom Box')

    volume_custom_box_min_x = fields.Float(string='Min X')
    volume_custom_box_min_y = fields.Float(string='Min Y')
    volume_custom_box_min_z = fields.Float(string='Min Z')

    volume_custom_box_max_x = fields.Float(string='Max X')
    volume_custom_box_max_y = fields.Float(string='Max Y')
    volume_custom_box_max_z = fields.Float(string='Max Z')

    # Axes
    axes_x_speed = fields.Char(string='X Axis Speed')
    axes_y_speed = fields.Char(string='Y Axis Speed')
    axes_z_speed = fields.Char(string='Z Axis Speed')
    axes_e_speed = fields.Char(string='E Axis Speed')

    axes_x_inverted = fields.Boolean(string='X Axis Inverted')
    axes_y_inverted = fields.Boolean(string='Y Axis Inverted')
    axes_z_inverted = fields.Boolean(string='Z Axis Inverted')
    axes_e_inverted = fields.Boolean(string='E Axis Inverted')

    # Extruder
    extruder_count = fields.Integer()
    extruder_shared_nozzle = fields.Boolean(string='Shared Nozzle', default=False)
    extruder_nozzle_diameter = fields.Float(string='Nozzle Diameter')
    extruder_nozzle_extrusion_length = fields.Float(string='Default Extrusion Length')
