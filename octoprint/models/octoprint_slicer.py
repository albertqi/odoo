from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
import requests

apikey = ''
API_BASE_URL = ''

class OctoPrintSlicer(models.Model):
    _name = 'octoprint.slicer'
    _description = 'OctoPrint Slicer'

    name = fields.Char(string='Name', required=True)
    printer_id = fields.Many2one('octoprint.printer')
    default = fields.Boolean(required=True)

    description = fields.Text(required=True)
    slicer_id = fields.Char(required=True)

    # Slicer Data TODO

    infill = fields.Integer(required=True)
    fill_density = fields.Integer(required=True)
    layer_height = fields.Float(default=0.2, required=True)
    skirt_line_count = fields.Integer(default=2, required=True)

    


    @api.model_create_multi
    def create(self, vals_list):
        res = super(OctoPrintSlicer, self).create(vals_list)
        for record in res:
            data = record._parse_to_JSON()
            response = requests.put(
                f'{API_BASE_URL}/api/slicing/curalegacy/profiles/{record.slicer_id}',
                params={
                    'apikey': apikey,
                },
                json=data,
            )
            response.raise_for_status()
            if response.status_code != 201:
                raise UserError(f"Bad Request: {response.json().get('error')}")
        return res

    def write(self, vals_list):
        res = super(OctoPrintSlicer, self).write(vals_list)
        for record in self:
            data = record._parse_to_JSON()
            response = requests.patch(
                f'{API_BASE_URL}/api/slicing/curalegacy/profiles/{record.slicer_id}',
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
                f'{API_BASE_URL}/api/slicing/curalegacy/profiles/{record.slicer_id}',
                params={'apikey': apikey},
            )
            if response.status_code == 409:
                raise UserError(f"Bad Request: The profile is the currently selected one!")
        return super(OctoPrintSlicer, self).unlink()

    def _parse_to_JSON(self):
        self.ensure_one()
        return {
            "displayName": self.name,
            "description": self.description,
            "default": self.default,
            "data": {
                "infill": self.infill,
                "fill_density": self.fill_density,
                "layer_height": self.layer_height,
                "skirt_line_count": self.skirt_line_count
            }
        }
