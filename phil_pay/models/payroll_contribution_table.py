from odoo import models, fields, api, _

class PayrollContributionSSS(models.Model):
	_name = 'payroll.contribution.sss'
	_description = 'SSS Contribution'

	range_from_amount = fields.Float(required=True)
	range_to_amount = fields.Float(required=True)
	monthly_salary_credit = fields.Float()
	er_amount = fields.Float(string='ER', required=True)
	ee_amount = fields.Float(string='EE', required=True)
	total_amount = fields.Float(string='Total')
	ec_amount = fields.Float(string='EC Contribution (ER)')