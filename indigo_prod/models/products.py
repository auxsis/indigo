from odoo import models, fields, api, _ 
from datetime import datetime

class IndigoProducts(models.Model):
	_inherit = 'product.template'

	@api.multi
	@api.depends('carmodel_group')
	def _compute_carmodel_group_id(self):
		for record in self:
			record.carmodel_group_id = record.carmodel_group and record.carmodel_group[0] or False

	color_type = fields.Char(
		string='Color or Type',
	)

	brand = fields.Many2one(
		'indigo_prod.brand',
		string='Brand',
	)

	brand_id = fields.Many2one(
		'indigo_prod.brand',
		string='Car Brand',
	)

	carmodel_id = fields.Many2one(
		'indigo_prod.carmodel',
		string='Car Model',
	)

	foreign_cost = fields.Float(
		string='Foreign Cost',
		groups="base.group_erp_manager"
	)

	exchange_rate = fields.Float(
		string='Exchange Rate',
		groups="base.group_erp_manager"
	)

	local_cost = fields.Float(
		string='Local Cost',
		store = True,
		compute = "_computed_local_cost",
		groups="base.group_erp_manager"
	)

	tags_ids = fields.Many2many(
		'indigo_prod.vehicle_tags',
		string='Vehicle Tags',
	)

	fit = fields.Selection([('one', 'One Fit'),('multiple', 'Multiple Fit'),])

	cartype_id = fields.Many2one('indigo_prod.cartype', string='Car Type')
	factory_id = fields.Many2one('indigo_prod.factory', string='Factory')
	country_id = fields.Many2one('res.country', string='Country')

	carmodel_group = fields.Many2many('indigo_prod.carmodelgroup', string='Car Model Group')
	carmodel_group_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group ID', compute="_compute_carmodel_group_id", store=True)

	# carmodel_group1_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group', compute="_compute_carmodel_group1_id", store=True)
	# carmodel_group2_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group 2')
	# carmodel_group3_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group 3') 

	floor_location = fields.Char()
	rack_location = fields.Char()

	carmodel_group = fields.Many2many('indigo_prod.carmodelgroup', string='Car Model Group')
	carmodel_year = fields.Integer(related='carmodel_id.year', string='Year')


	@api.depends('foreign_cost', 'exchange_rate')
	def _computed_local_cost(self):
		for record in self:
			record.local_cost = record.foreign_cost * record.exchange_rate
			record.standard_price = record.local_cost

	
	@api.onchange('factory_id')
	def get_country(self):
		self.country_id = self.factory_id.country_id


class VehicleTags(models.Model):
	_name = 'indigo_prod.vehicle_tags'

	name = fields.Char(
		string='',
		size=64,
		required=False
		)

class IndigoBrand(models.Model):
	_name = 'indigo_prod.brand'
	_description = 'Car Brands'

	name = fields.Char(
		string='Brand Name',
		required=True
		)

class IndigoModel(models.Model):
	_name = 'indigo_prod.carmodel'
	_description = 'Car models'

	name = fields.Char(string='Vehicle Model Name', required=True)
	# year = fields.Selection([(int(num), str(num)) for num in range(1900, (datetime.now().year)+1 )], string='Year', default=datetime.now().year)
	# year = fields.Date()
	year = fields.Integer()

class IndigoModelGroup(models.Model):
	_name = 'indigo_prod.carmodelgroup'
	_description = 'Car Model Group'

	name = fields.Char(string='Car Model Group', required=True)

class IndigoCarType(models.Model):
	_name = 'indigo_prod.cartype'
	_description = 'Car Types'

	name = fields.Char(string='Car Type', required=True)

class IndigoFactory(models.Model):
	_name = 'indigo_prod.factory'
	_description = 'Factories'

	name = fields.Char(string='Factory', required=True)
	country_id = fields.Many2one('res.country', string='Country')