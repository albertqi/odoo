from odoo import api, models, fields
from odoo.exceptions import UserError
import requests
import io


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
        required=True,
    )
    completion = fields.Float()
    current_print_time = fields.Integer()
    remaining_print_time = fields.Integer()
    is_current_job = fields.Boolean(compute='_compute_fields')

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
            file = io.BytesIO(self.stl_file)
            file.name = (
                f'{self.name}.stl'  # STL file will be named after the print name.
            )
            file.seek(0)
            response = requests.post(
                f'{icp_sudo.get_param("octoprint.base_url")}/api/files/local',
                params={
                    'apikey': icp_sudo.get_param('octoprint.api_key'),
                },
                files={
                    'file': io.BufferedReader(file),
                },
            )
            response.raise_for_status()
        except:
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
        record.completion = job['progress']['completion']
        record.current_print_time = job['progress']['printTime']
        record.remaining_print_time = job['progress']['printTimeLeft']

        if job['progress']['completion'] >= 1.0:
            record.state = 'done'
        elif printer['state']['flags']['error']:
            record.state = 'error'
        elif printer['state']['flags']['cancelling']:
            record.state = 'cancel'
        else:
            record.state = 'printing'

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
