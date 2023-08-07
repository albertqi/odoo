from odoo import api, models, fields
from odoo.exceptions import UserError
import requests
import io


apikey = ''
API_BASE_URL = ''


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
        compute='_compute_state',
    )
    completion = fields.Float(compute='_compute_progress')
    current_print_time = fields.Integer(compute='_compute_progress')
    remaining_print_time = fields.Integer(compute='_compute_progress')

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
        try:
            file = io.BytesIO(self.stl_file)
            file.name = (
                f'{self.name}.stl'  # STL file will be named after the print name
            )
            file.seek(0)
            response = requests.post(
                f'{API_BASE_URL}/api/files/local',
                params={
                    'apikey': apikey,
                },
                files={
                    'file': io.BufferedReader(file),
                },
            )
            response.raise_for_status()
        except:
            raise UserError(f"Bad Request: {response.json().get('error')}")

    def _compute_state(self):
        job = self._get_job()
        for record in self:
            if job['job']['file']['name'] == f'{record.name}.gco':
                if job['state'] == 'Error':
                    record.state = 'error'
                elif job['state'] == 'Cancelling':
                    record.state = 'cancel'
            else:
                record.state = record.state

    def _compute_progress(self):
        # TODO: Change from job operation to printer operation
        job = self._get_job()
        for record in self:
            if job['job']['file']['name'] == f'{record.name}.gco':
                record.completion = job['progress']['completion']
                record.current_print_time = job['progress']['printTime']
                record.remaining_print_time = job['progress']['printTimeLeft']
            else:
                record.completion = record.completion
                record.current_print_time = record.current_print_time
                record.remaining_print_time = record.remaining_print_time

    def _get_job(self):
        response = None
        try:
            response = requests.get(
                f'{API_BASE_URL}/api/job',
                params={
                    'apikey': apikey,
                },
            )
            response.raise_for_status()
            return response.json()
        except:
            raise UserError(f"Bad Request: {response.json().get('error')}")

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
        try:
            response = requests.post(
                f'{API_BASE_URL}/api/files/local/{self.stl_file_name}',
                params={
                    'apikey': apikey,
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
