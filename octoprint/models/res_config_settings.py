from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    octoprint_base_url = fields.Char('OctoPrint Base URL', store=True)
    octoprint_api_key = fields.Char('OctoPrint API Key', store=True)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'octoprint.base_url', self.octoprint_base_url
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'octoprint.api_key', self.octoprint_api_key
        )
        self.octoprint_base_url = self.env['ir.config_parameter'].get_param(
            'octoprint.base_url'
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        res.update(
            octoprint_base_url=icp_sudo.get_param('octoprint.base_url'),
            octoprint_api_key=icp_sudo.get_param('octoprint.api_key'),
        )
        return res
