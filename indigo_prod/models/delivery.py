from odoo import models, fields, api, _ 

class DeliveryCarrier(models.Model):
	_inherit = 'delivery.carrier'

	partner_id = fields.Many2one('res.partner', string='Forwarder')
	default = fields.Boolean()