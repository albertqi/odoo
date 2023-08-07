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
        try:
            file = io.BytesIO(self.stl_file)
            file.name = self.stl_file_name
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
        # TODO: API call using GET /api/job
        # Returns only the currently printing job

        for record in self:
            record.state = 'open'

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
