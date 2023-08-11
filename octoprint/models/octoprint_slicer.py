from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
import requests


class OctoPrintSlicer(models.Model):
    _name = 'octoprint.slicer'
    _description = 'OctoPrint Slicer'

    name = fields.Char(string='Name', required=True)
    default = fields.Boolean(required=True)

    description = fields.Text(required=True)
    slicer_id = fields.Char(required=True)
    printer_id = fields.Many2one('octoprint.printer', required=True)

    # extruder_ids = fields.One2many('octoprint.slicer.extruder', 'slicer_id', string='Extruders', required=True)
    print_temperature = fields.Integer(default=210, required=True)
    extruder_filament_diameter = fields.Float(default=2.85, required=True)

    # Slicer Data TODO
    layer_height = fields.Float(default=0.2, required=True)
    wall_thickness = fields.Float(default=1.0,required=True)
    retraction_enable = fields.Boolean(default=True,required=True)
    solid_layer_thickness = fields.Float(default=0.6,required=True)
    fill_density = fields.Integer(default=30,required=True)

    # Print stuff
    print_speed = fields.Integer(default=50,required=True)
    print_bed_temperature = fields.Integer(default=70,required=True)
    # Support
    support = fields.Selection([
        ('none', 'None'),
        ('buildplate', 'Buildplate Only'),
        ('everywhere', 'Everywhere')
    ], default='none', required=True)
    support_type = fields.Selection([
        ('lines', 'Lines'),
        ('grid', 'Grid')
    ], default='lines', required=True) 
    support_angle = fields.Integer(default=60,required=True)
    support_fill_rate = fields.Integer(default=15,required=True)
    support_xy_distance = fields.Integer(default=0.7,required=True)
    support_z_distance = fields.Integer(default=0.15,required=True)
    spiralization = fields.Boolean(required=True)

    # Raft
    platform_adhesion = fields.Selection([
        ('none', 'None'),
        ('brim', 'Brim'),
        ('raft', 'Raft')
    ], default='none', required=True)
    raft_margin = fields.Float(default=5.0,required=True)
    raft_line_spacing = fields.Float(default=3.0,required=True)
    raft_base_thickness = fields.Float(default=0.3,required=True)
    raft_base_linewidth = fields.Float(default=1.0,required=True)
    raft_interface_thickness = fields.Float(default=0.27,required=True)
    raft_interface_linewidth = fields.Float(default=0.4,required=True)
    raft_airgap = fields.Float(default=0.22,required=True)
    raft_surface_layers = fields.Integer(default=2,required=True)
    raft_surface_thickness = fields.Integer(default=0.27,required=True)
    raft_surface_linewidth = fields.Integer(default=0.4,required=True)

    skirt_line_count = fields.Integer(default=2, required=True)
    skirt_gap = fields.Float(default=3.0,required=True)
    skirt_minimal_length = fields.Float(default=150.0,required=True)

    
    # Wipe tower
    wipe_tower = fields.Boolean(required=True)
    wipe_tower_volume = fields.Integer(default=15,required=True)
    ooze_shield = fields.Boolean(required=True)
    
    nozzle_size = fields.Float(related="printer_id.nozzle_diameter",required=True)

    # Retraction
    retraction_speed = fields.Integer(default=40.0,required=True)
    retraction_amount = fields.Float(default=4.5,required=True)
    retraction_dual_amount = fields.Float(default=16.5,required=True)
    retraction_min_travel = fields.Float(default=1.5,required=True)
    retraction_minimal_extrusion = fields.Float(default=0.02,required=True)
    retraction_hop = fields.Float(default=0.0,required=True)
    bottom_thickness = fields.Float(default=0.3,required=True)
    layer0_width_factor = fields.Float(default=100,required=True)

    # Fan
    fan_speed = fields.Integer(default=100,required=True)
    fan_speed_max = fields.Integer(default=100,required=True)
    cool_min_feedrate = fields.Integer(default=10,required=True)
    

    # Parameters
    start_gcode = fields.Text(required=True)
    end_gcode = fields.Text(required=True)
    @api.model_create_multi
    def create(self, vals_list):
        res = super(OctoPrintSlicer, self).create(vals_list)
        icp_sudo = self.env['ir.config_parameter'].sudo()
        for record in res:
            data = record._parse_to_JSON()
            response = requests.put(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/slicing/curalegacy/profiles/{record.slicer_id}',
                params={
                    'apikey': icp_sudo.get_param("octoprint.api_key"),
                },
                json=data,
            )
            response.raise_for_status()
            if response.status_code != 201:
                raise UserError(f"Bad Request: {response.json().get('error')}")
        return res

    def write(self, vals_list):
        res = super(OctoPrintSlicer, self).write(vals_list)
        icp_sudo = self.env['ir.config_parameter'].sudo()
        for record in self:
            data = record._parse_to_JSON()
            response = requests.patch(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/slicing/curalegacy/profiles/{record.slicer_id}',
                params={
                    'apikey': icp_sudo.get_param("octoprint.api_key"),
                },
                json=data,
            )
            if response.status_code != 200:
                raise UserError(f"Bad Request: {response.json().get('error')}")
        return res

    def unlink(self):
        icp_sudo = self.env['ir.config_parameter'].sudo()
        for record in self:
            response = requests.delete(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/slicing/curalegacy/profiles/{record.slicer_id}',
                params={'apikey': icp_sudo.get_param("octoprint.api_key")},
            )
            if response.status_code == 409:
                raise UserError(
                    f"Bad Request: The profile is the currently selected one!"
                )
        return super(OctoPrintSlicer, self).unlink()

    def _parse_to_JSON(self):
        self.ensure_one()
        print(self.print_temperature)
        return {
            "displayName": self.name,
            "description": self.description,
            "default": self.default,
            "data": {
                "layer_height": self.layer_height,
                "wall_thickness": self.wall_thickness,
                "retraction_enable": self.retraction_enable,
                "solid_layer_thickness": self.solid_layer_thickness,
                "fill_density": self.fill_density,

                "print_speed": self.print_speed,
                "print_temperature":[
                    self.print_temperature,
                    False,
                    False,
                    False
                ],
                "print_bed_temperature": self.print_bed_temperature,

                "support": self.support,
                "support_type": self.support_type,
                "support_angle": self.support_angle,
                "support_fill_rate": self.support_fill_rate,
                "support_xy_distance": self.support_xy_distance,
                "support_z_distance": self.support_z_distance,
                "spiralization": self.spiralization,
                "platform_adhesion": self.platform_adhesion,

                "raft_margin": self.raft_margin,
                "raft_line_spacing": self.raft_line_spacing,
                "raft_base_thickness": self.raft_base_thickness,
                "raft_base_linewidth": self.raft_base_linewidth,
                "raft_interface_thickness": self.raft_interface_thickness,
                "raft_interface_linewidth": self.raft_interface_linewidth,
                "raft_airgap": self.raft_airgap,
                "raft_surface_layers": self.raft_surface_layers,
                "raft_surface_thickness": self.raft_surface_thickness,
                "raft_surface_linewidth": self.raft_surface_linewidth,

                "skirt_line_count": self.skirt_line_count,
                "skirt_gap": self.skirt_gap,
                "skirt_minimal_length": self.skirt_minimal_length,

                "wipe_tower": self.wipe_tower,
                "wipe_tower_volume": self.wipe_tower_volume,
                "ooze_shield": self.ooze_shield,

                "nozzle_size":self.nozzle_size,

                "retraction_speed":self.retraction_speed,
                "retraction_amount":self.retraction_amount,
                "retraction_dual_amount":self.retraction_dual_amount,
                "retraction_min_travel":self.retraction_min_travel,
                "retraction_minimal_extrusion":self.retraction_minimal_extrusion,
                "retraction_hop":self.retraction_hop,

                "bottom_thickness":self.bottom_thickness,

                "layer0_width_factor":self.layer0_width_factor,
                "fan_speed": self.fan_speed,
                "fan_speed_max": self.fan_speed_max,
                "cool_min_feedrate": self.cool_min_feedrate,

                "start_gcode": [self.start_gcode],
                "end_gcode" : [self.end_gcode],
                
            },
        }
