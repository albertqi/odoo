from odoo import api, models, fields

class OctoprintPrint(models.Model):
    _name = "octoprint.print"
    _description = "Octoprint Print"
    

    name = fields.Char(string="Name", required=True)
    mrp_id = fields.Many2one(comodel_name='mrp.production', string="Manufacturing Order", required=True)
    state = fields.Char(string="State", compute="_compute_state")



    def _compute_state(self):
        self.ensure_one()
        #TODO: API call using GET /api/job
        # returns only the currently printing job
        self.state = "Printing"