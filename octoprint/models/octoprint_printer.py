from odoo import api, models, fields
from odoo.exceptions import ValidationError, UserError
import requests

apikey = ''
API_BASE_URL = ''


class OctoPrintPrinter(models.Model):
    _name = 'octoprint.printer'
    _description = 'OctoPrint Printer'

    name = fields.Char(required=True)

    # General
    profile_id = fields.Char(required=True)
    model = fields.Char(required=True)

    # Printer Bed
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
    default = fields.Boolean(required=True)
    current = fields.Boolean(required=True)
    heated_bed = fields.Boolean(default=True, required=True)
    heated_chamber = fields.Boolean(required=True)

    # Build Volume
    form_factor = fields.Selection(
        [
            ('rectangular', 'Rectangular'),
            ('circular', 'Circular'),
        ],
        default='rectangular',
        required=True,
    )
    origin = fields.Selection(
        [
            ('lowerleft', 'Lower Left'),
            ('center', 'Center'),
        ],
        default='lowerleft',
        required=True,
    )

    width = fields.Float(default=200.0, required=True)
    depth = fields.Float(default=200.0, required=True)
    height = fields.Float(default=200.0, required=True)

    custom_box = fields.Boolean(string='Custom Bounding Box', required=True)

    min_x = fields.Float()
    min_y = fields.Float()
    min_z = fields.Float()

    max_x = fields.Float()
    max_y = fields.Float()
    max_z = fields.Float()

    # Axes
    x_speed = fields.Integer(default=6000, required=True)
    y_speed = fields.Integer(default=6000, required=True)
    z_speed = fields.Integer(default=200, required=True)
    e_speed = fields.Integer(default=300, required=True)

    x_inverted = fields.Boolean(required=True)
    y_inverted = fields.Boolean(required=True)
    z_inverted = fields.Boolean(required=True)
    e_inverted = fields.Boolean(required=True)

    # Extruder
    extruder_count = fields.Integer(
        default=1, string='Number of Extruders', required=True
    )
    shared_nozzle = fields.Boolean(required=True)
    nozzle_diameter = fields.Float(required=True)
    nozzle_length = fields.Integer(
        default=5, string='Default Extrusion Length', required=True
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
            response.raise_for_status()
            if response.status_code != 200:
                raise UserError(f"Bad Request: {response.json().get('error')}")
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
            if response.status_code != 200:
                raise UserError(f"Bad Request: {response.json().get('error')}")
        return res

    def unlink(self):
        for record in self:
            response = requests.delete(
                f'{API_BASE_URL}/api/printerprofiles/{record.profile_id}',
                params={'apikey': apikey},
            )
            if response.status_code == 409:
                raise UserError(
                    f"Bad Request: The profile is the currently selected one!"
                )
        return super(OctoPrintPrinter, self).unlink()

    @api.constrains('width', 'depth', 'height')
    def _check_volume_dimensions(self):
        for record in self:
            if record.width <= 0:
                raise ValidationError('The width must be positive.')
            if record.depth <= 0:
                raise ValidationError('The depth must be positive.')
            if record.height <= 0:
                raise ValidationError('The height must be positive.')

    @api.constrains('custom_box', 'min_x', 'min_y', 'min_z', 'max_x', 'max_y', 'max_z')
    def _check_custom_box(self):
        for record in self:
            if record.custom_box:
                if record.min_x > 0:
                    raise ValidationError('The min X must be less than or equal to 0.')
                if record.min_y > 0:
                    raise ValidationError('The min Y must be less than or equal to 0.')
                if record.min_z > 0:
                    raise ValidationError('The min Z must be less than or equal to 0.')
                if record.max_x < record.width:
                    raise ValidationError(
                        f'The max X must be greater than or equal to {record.width}.'
                    )
                if record.max_y < record.depth:
                    raise ValidationError(
                        f'The max Y must be greater than or equal to {record.depth}.'
                    )
                if record.max_z < record.height:
                    raise ValidationError(
                        f'The max Z must be greater than or equal to {record.height}.'
                    )

    @api.constrains('x_speed', 'y_speed', 'z_speed', 'e_speed')
    def _check_axes_speed(self):
        for record in self:
            if record.x_speed <= 0:
                raise ValidationError('The X axis speed must be positive.')
            if record.y_speed <= 0:
                raise ValidationError('The Y axis speed must be positive.')
            if record.z_speed <= 0:
                raise ValidationError('The Z axis speed must be positive.')
            if record.e_speed <= 0:
                raise ValidationError('The E axis speed must be positive.')

    @api.constrains('extruder_count', 'extruder_ids')
    def _check_extruders(self):
        for record in self:
            if record.extruder_count < 1:
                raise ValidationError('You must have at least 1 extruder.')
            if record.extruder_count != len(record.extruder_ids):
                raise ValidationError(
                    'The number of extruders does not match the count.'
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
                'heatedBed': self.heated_bed,
                'heatedChamber': self.heated_chamber,
                'axes': {
                    'x': {
                        'speed': self.x_speed,
                        'inverted': self.x_inverted,
                    },
                    'y': {
                        'speed': self.y_speed,
                        'inverted': self.y_inverted,
                    },
                    'z': {
                        'speed': self.z_speed,
                        'inverted': self.z_inverted,
                    },
                    'e': {
                        'speed': self.e_speed,
                        'inverted': self.e_inverted,
                    },
                },
                'volume': {
                    'formFactor': self.form_factor,
                    'origin': self.origin,
                    'width': self.width,
                    'depth': self.depth,
                    'height': self.height,
                    'custom_box': {
                        'x_min': self.min_x,
                        'y_min': self.min_y,
                        'z_min': self.min_z,
                        'x_max': self.max_x,
                        'y_max': self.max_y,
                        'z_max': self.max_z,
                    }
                    if self.custom_box
                    else False,
                },
                'extruder': {
                    'count': self.extruder_count,
                    'sharedNozzle': self.shared_nozzle,
                    'nozzleDiameter': self.nozzle_diameter,
                    'defaultExtrusionLength': self.nozzle_length,
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
