from odoo import api, models, fields
from odoo.exceptions import ValidationError
import requests

apikey = ''
API_BASE_URL = ''


class OctoPrintPrinter(models.Model):
    _name = 'octoprint.printer'
    _description = 'OctoPrint Printer'

    name = fields.Char(required=True)
    slicer_ids = fields.One2many('octoprint.slicer', 'printer_id', string='Slicers')
    slicer_count = fields.Integer(compute='_compute_slicer_count')

    # Printer Data
    profile_id = fields.Char(required=True)
    color = fields.Selection(
        [
            ('default', 'Default'),
            ('red', 'Red'),
            ('orange', 'Orange'),
            ('yellow', 'Yellow'),
            ('green', 'Green'),
            ('blue', 'Blue'),
            ('black', 'Black'),
        ],
        default='default',
        required=True,
    )
    model = fields.Char(required=True)
    default = fields.Boolean(required=True)
    current = fields.Boolean(required=True)
    has_heated_bed = fields.Boolean(default=True, required=True)
    has_heated_chamber = fields.Boolean(required=True)

    # Volume
    volume_form_factor = fields.Selection(
        [
            ('rectangular', 'Rectangular'),
            ('circular', 'Circular'),
        ],
        default='rectangular',
        string='Form Factor',
        required=True,
    )
    volume_origin = fields.Selection(
        [
            ('lowerleft', 'Lower Left'),
            ('center', 'Center'),
        ],
        default='lowerleft',
        string='Origin',
        required=True,
    )
    volume_width = fields.Float(default=200.0, string='Width', required=True)
    volume_depth = fields.Float(default=200.0, string='Depth', required=True)
    volume_height = fields.Float(default=200.0, string='Height', required=True)
    volume_custom_box = fields.Boolean(string='Custom Box', required=True)

    volume_custom_box_min_x = fields.Float(string='Min X')
    volume_custom_box_min_y = fields.Float(string='Min Y')
    volume_custom_box_min_z = fields.Float(string='Min Z')

    volume_custom_box_max_x = fields.Float(string='Max X')
    volume_custom_box_max_y = fields.Float(string='Max Y')
    volume_custom_box_max_z = fields.Float(string='Max Z')

    # Axes
    axes_x_speed = fields.Integer(string='X Axis Speed', required=True)
    axes_y_speed = fields.Integer(string='Y Axis Speed', required=True)
    axes_z_speed = fields.Integer(string='Z Axis Speed', required=True)
    axes_e_speed = fields.Integer(string='E Axis Speed', required=True)

    axes_x_inverted = fields.Boolean(string='X Axis Inverted', required=True)
    axes_y_inverted = fields.Boolean(string='Y Axis Inverted', required=True)
    axes_z_inverted = fields.Boolean(string='Z Axis Inverted', required=True)
    axes_e_inverted = fields.Boolean(string='E Axis Inverted', required=True)

    # Extruder
    extruder_count = fields.Integer(required=True)
    extruder_shared_nozzle = fields.Boolean(string='Shared Nozzle', required=True)
    extruder_nozzle_diameter = fields.Float(string='Nozzle Diameter', required=True)
    extruder_nozzle_length = fields.Integer(
        string='Default Extrusion Length', required=True
    )
    extruder_ids = fields.One2many(
        'octoprint.extruder', 'printer_id', string='Extruders'
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(OctoPrintPrinter, self).create(vals_list)
        for record in res:
            data = record._parse_to_JSON()
            response = requests.post(
                f'{API_BASE_URL}/api/printerprofiles',
                params={
                    'apikey': apikey,
                },
                json=data,
            )
        return res

    def write(self, vals_list):
        res = super(OctoPrintPrinter, self).write(vals_list)
        for record in self:
            data = record._parse_to_JSON()
            response = requests.patch(
                f'{API_BASE_URL}/api/printerprofiles/{record.profile_id}',
                params={
                    'apikey': apikey,
                },
                json=data,
            )
        return res

    def unlink(self):
        for record in self:
            response = requests.delete(
                f'{API_BASE_URL}/api/printerprofiles/{record.profile_id}',
                params={'apikey': apikey},
            )
        return super(OctoPrintPrinter, self).unlink()

    @api.depends('slicer_ids')
    def _compute_slicer_count(self):
        for record in self:
            record.slicer_count = len(record.slicer_ids)

    def action_view_slicers(self):
        self.ensure_one()
        return {
            'name': 'Slicers',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'octoprint.slicer',
            'domain': [('printer_id', '=', self.id)],
        }

    @api.constrains('volume_width', 'volume_depth', 'volume_height')
    def _check_volume_dimensions(self):
        for record in self:
            if record.volume_width <= 0:
                raise ValidationError('The width must be positive.')
            if record.volume_depth <= 0:
                raise ValidationError('The depth must be positive.')
            if record.volume_height <= 0:
                raise ValidationError('The height must be positive.')

    @api.constrains('extruder_count', 'extruder_ids')
    def _check_extruders(self):
        for record in self:
            if record.extruder_count < 1:
                raise ValidationError('The number of extruders must be at least 1.')
            if record.extruder_count != len(record.extruder_ids):
                raise ValidationError(
                    'The number of extruders does not match the count.'
                )

    @api.constrains(
        'volume_custom_box',
        'volume_custom_box_min_x',
        'volume_custom_box_min_y',
        'volume_custom_box_min_z',
        'volume_custom_box_max_x',
        'volume_custom_box_max_y',
        'volume_custom_box_max_z',
    )
    def _check_custom_box(self):
        for record in self:
            if record.volume_custom_box:
                if record.volume_custom_box_min_x > 0:
                    raise ValidationError('The min X must be less than or equal to 0.')
                if record.volume_custom_box_min_y > 0:
                    raise ValidationError('The min Y must be less than or equal to 0.')
                if record.volume_custom_box_min_z > 0:
                    raise ValidationError('The min Z must be less than or equal to 0.')
                if record.volume_custom_box_max_x < record.volume_width:
                    raise ValidationError(
                        f'The max X must be greater than or equal to {record.volume_width}.'
                    )
                if record.volume_custom_box_max_y < record.volume_depth:
                    raise ValidationError(
                        f'The max Y must be greater than or equal to {record.volume_depth}.'
                    )
                if record.volume_custom_box_max_z < record.volume_height:
                    raise ValidationError(
                        f'The max Z must be greater than or equal to {record.volume_height}.'
                    )

    def _parse_to_JSON(self):
        self.ensure_one()
        return {
            'profile': {
                'id': self.profile_id,
                'name': self.name,
                'color': self.color,
                'model': self.model,
                'default': self.default,
                'current': self.current,
                'heatedBed': self.has_heated_bed,
                'heatedChamber': self.has_heated_chamber,
                'axes': {
                    'x': {
                        'speed': self.axes_x_speed,
                        'inverted': self.axes_x_inverted,
                    },
                    'y': {
                        'speed': self.axes_y_speed,
                        'inverted': self.axes_y_inverted,
                    },
                    'z': {
                        'speed': self.axes_z_speed,
                        'inverted': self.axes_z_inverted,
                    },
                    'e': {
                        'speed': self.axes_e_speed,
                        'inverted': self.axes_e_inverted,
                    },
                },
                'volume': {
                    'formFactor': self.volume_form_factor,
                    'origin': self.volume_origin,
                    'width': self.volume_width,
                    'depth': self.volume_depth,
                    'height': self.volume_height,
                    'custom_box': {
                        'x_min': self.volume_custom_box_min_x,
                        'y_min': self.volume_custom_box_min_y,
                        'z_min': self.volume_custom_box_min_z,
                        'x_max': self.volume_custom_box_max_x,
                        'y_max': self.volume_custom_box_max_y,
                        'z_max': self.volume_custom_box_max_z,
                    }
                    if self.volume_custom_box
                    else False,
                },
                'extruder': {
                    'count': self.extruder_count,
                    'sharedNozzle': self.extruder_shared_nozzle,
                    'nozzleDiameter': self.extruder_nozzle_diameter,
                    'defaultExtrusionLength': self.extruder_nozzle_length,
                    'offsets': [
                        [
                            extruder.x_offset,
                            extruder.y_offset,
                        ]
                        for extruder in self.extruder_ids
                    ],
                },
            },
        }
