from odoo import models, fields, api

class HREmployee(models.Model):
	_inherit = 'hr.employee'

	address_provincial_id = fields.Many2one('res.partner', 'Provincial Address', help='Enter here the provincial address of the employee, not the one linked to your company.')