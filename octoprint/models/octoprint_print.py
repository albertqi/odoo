from odoo import api, models, fields
from odoo import Command
from odoo.exceptions import UserError
import requests
import base64

class OctoPrintPrint(models.Model):
    _name = 'octoprint.print'
    _description = 'OctoPrint Print'

    name = fields.Char(default='New', required=True, copy=False, readonly=True)
    mrp_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    stl_file = fields.Binary(string='STL File')
    stl_file_name = fields.Char(string='STL File Name')
    slicer_id = fields.Many2one('octoprint.slicer')
    printer_id = fields.Many2one('octoprint.printer')
    state = fields.Selection(
        [
            ('open', 'Open'),
            ('print', 'Printing'),
            ('done', 'Finished'),
            ('error', 'Error'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='open',
        readonly=True,
        required=True,
    )
    completion = fields.Float(readonly=True)
    current_print_time = fields.Integer(readonly=True)
    remaining_print_time = fields.Integer(readonly=True)
    is_current_job = fields.Boolean(compute='_compute_fields')
    statistic_ids = fields.One2many(
        'octoprint.statistic', 'print_id', string='Statistics', readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('octoprint.print')
        res = super(OctoPrintPrint, self).create(vals_list)
        for record in res:
            record._upload_file()
        return res

    def write(self, vals_list):
        res = super(OctoPrintPrint, self).write(vals_list)
        for record in self:
            record._upload_file()
        return res

    def _upload_file(self):
        self.ensure_one()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        try:
            file = base64.b64decode(self.stl_file)
            response = requests.post(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/files/local',
                params={
                    'apikey': icp_sudo.get_param('octoprint.api_key'),
                },
                files={"file": (f'{self.name}.stl', file)},
            )
            response.raise_for_status()
        except Exception as e:
            print(e)
            raise UserError(f"Bad Request: {response.json().get('error')}")

    def _compute_fields(self):
        icp_sudo = self.env['ir.config_parameter'].sudo()
        for record in self:
            record.is_current_job = False

        # Get the current job from OctoPrint.
        response = job = None
        try:
            response = requests.get(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/job',
                params={
                    'apikey': icp_sudo.get_param("octoprint.api_key"),
                },
            )
            response.raise_for_status()
            job = response.json()
        except:
            raise UserError(f"Bad Request: {response.json().get('error')}")

        # Get the current printer from OctoPrint.
        response = printer = None
        try:
            response = requests.get(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/printer',
                params={
                    'apikey': icp_sudo.get_param("octoprint.api_key"),
                },
            )
            response.raise_for_status()
            printer = response.json()
        except:
            raise UserError(f"Bad Request: {response.json().get('error')}")

        # Update the current job.
        record = self.filtered(lambda r: job['job']['file']['name'] == f'{r.name}.gco')
        if not record:
            return

        record.is_current_job = True
        record.completion = job['progress']['completion'] / 100.0
        record.current_print_time = job['progress']['printTime']
        record.remaining_print_time = job['progress']['printTimeLeft']

        if record.state == 'cancel':
            pass
        elif job['progress']['completion'] >= 100.0:
            record.state = 'done'
        elif printer['state']['flags']['error']:
            record.state = 'error'
        else:
            record.state = 'print'

        def create_statistic(name, dict):
            return {
                'name': name,
                'actual_temperature': dict.get('actual', 0.0),
                'target_temperature': dict.get('target', 0.0),
                'temperature_offset': dict.get('offset', 0.0),
                'filament_length': dict.get('length', 0.0),
                'filament_volume': dict.get('volume', 0.0),
            }

        statistics = {}
        for key, value in printer['temperature'].items():
            if not (key == 'bed' or key.startswith('tool')):
                continue
            statistics[key] = value
        for key, value in job['job']['filament'].items():
            statistics[key] = statistics.get(key, {}) | value
        record.statistic_ids = [
            Command.delete(statistic.id) for statistic in record.statistic_ids
        ]
        record.statistic_ids = [
            Command.create(create_statistic(name, dict))
            for name, dict in statistics.items()
        ]

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_print(self):
        if len(self) != 1:
            raise UserError('Please select exactly one record to print.')
        if self.state != 'open':
            raise UserError('Please select an open record to print.')
        domain = [('state', '=', 'printing'), ('printer_id', '=', self.printer_id.id)]
        if len(self.env['octoprint.print'].search(domain)) > 0:
            raise UserError('Please wait for the current print to finish.')
        if not (self.stl_file and self.slicer_id and self.printer_id):
            raise UserError(
                'Please upload an STL file and select a slicer and printer.'
            )

        # Issue print command
        icp_sudo = self.env['ir.config_parameter'].sudo()
        response = None
        try:
            response = requests.post(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/files/local/{self.name}.stl',
                params={
                    'apikey': icp_sudo.get_param('octoprint.api_key'),
                },
                json={
                    'command': 'slice',
                    'slicer': 'curalegacy',
                    'printerProfile': self.printer_id.profile_id,
                    'profile': self.slicer_id.slicer_id,
                    'print': True,
                },
            )
            response.raise_for_status()
        except:
            raise UserError(f"Bad Request: {response.json().get('error')}")
