# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

class StockoutOrder(models.Model):
	_name = 'stockout.order'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_description = 'Stockout Order'
	_order = 'id desc'

	@api.depends('order_line.price_total')
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			order.update({
				'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
				'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
				'amount_total': amount_untaxed + amount_tax,
			})

	@api.model
	def _default_note(self):
		return self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note') and self.env.user.company_id.sale_note or ''

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
	confirmation_date = fields.Datetime(string='Confirmation Date', readonly=True, index=True, help="Date on which the stockout order is confirmed.")
	legacy_number = fields.Char(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]}, required=True, index=True)
	user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', default=lambda self: self.env.user)
	partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	order_line = fields.One2many('stockout.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Pricelist for current stockout order.")
	currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)

	amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='onchange')
	amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
	amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')

	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))

	note = fields.Text('Terms and conditions', default=_default_note)

	@api.multi
	@api.onchange('partner_id')
	def onchange_partner_id(self):
		values = {
			'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
			'user_id': self.partner_id.user_id.id or self.env.uid
		}
		if self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note') and self.env.user.company_id.sale_note:
			values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note

		self.update(values)

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			if 'company_id' in vals:
				vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('stockout.order') or _('New')
			else:
				vals['name'] = self.env['ir.sequence'].next_by_code('stockout.order') or _('New')

		# Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
		if any(f not in vals for f in ['pricelist_id']):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
		result = super(StockoutOrder, self).create(vals)
		return result

	@api.multi
	def action_confirm(self):
		for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
			order.message_subscribe([order.partner_id.id])
		self.write({
			'state': 'confirm',
			'confirmation_date': fields.Datetime.now()
		})

		return True

class StockoutOrderLine(models.Model):
	_name = 'stockout.order.line'
	_description = 'Stockout Order Line'
	_order = 'order_id, sequence, id'

	
	@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		"""
		Compute the amounts of the SO line.
		"""
		for line in self:
			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
			line.update({
				'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
				'price_total': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
			})

	@api.depends('price_unit', 'discount')
	def _get_price_reduce(self):
		for line in self:
			line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

	@api.depends('price_total', 'product_uom_qty')
	def _get_price_reduce_tax(self):
		for line in self:
			line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

	@api.depends('price_subtotal', 'product_uom_qty')
	def _get_price_reduce_notax(self):
		for line in self:
			line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

	@api.multi
	def _compute_tax_id(self):
		for line in self:
			fpos = line.order_id.partner_id.property_account_position_id
			# If company_id is set, always filter taxes by the company
			taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
			line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

	@api.model
	def _prepare_add_missing_fields(self, values):
		""" Deduce missing required fields from the onchange """
		res = {}
		onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
		if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
			line = self.new(values)
			line.product_id_change()
			for field in onchange_fields:
				if field not in values:
					res[field] = line._fields[field].convert_to_write(line[field], line)
		return res

	@api.model
	def create(self, values):
		values.update(self._prepare_add_missing_fields(values))
		line = super(StockoutOrderLine, self).create(values)
		return line

	order_id = fields.Many2one('stockout.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
	name = fields.Text(string='Description', required=True)
	sequence = fields.Integer(string='Sequence', default=10)

	price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

	currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
	company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)

	price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
	price_tax = fields.Float(compute='_compute_amount', string='Taxes', readonly=True, store=True)
	price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

	price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce', digits=dp.get_precision('Product Price'), readonly=True, store=True)
	tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
	price_reduce_taxinc = fields.Monetary(compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True, store=True)
	price_reduce_taxexcl = fields.Monetary(compute='_get_price_reduce_notax', string='Price Reduce Tax excl', readonly=True, store=True)

	discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)

	product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
	product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
	product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)

	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
	], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

	@api.multi
	def _get_display_price(self, product):
		# TO DO: move me in master/saas-16 on sale.order
		if self.order_id.pricelist_id.discount_policy == 'with_discount':
			return product.with_context(pricelist=self.order_id.pricelist_id.id).price
		final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
		pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
		if pricelist_item.base == 'pricelist':
			base_price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
			base_price = pricelist_item.base_pricelist_id.currency_id.compute(base_price, self.order_id.pricelist_id.currency_id)
		else:
			base_price = product[pricelist_item.base] if pricelist_item else product.lst_price
			base_price = product.currency_id.compute(base_price, self.order_id.pricelist_id.currency_id)
		# negative discounts (= surcharge) are included in the display price (= unit price)
		return max(base_price, final_price)

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		if not self.product_id:
			return {'domain': {'product_uom': []}}

		vals = {}
		domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
			vals['product_uom'] = self.product_id.uom_id
			vals['product_uom_qty'] = 1.0

		product = self.product_id.with_context(
			lang=self.order_id.partner_id.lang,
			partner=self.order_id.partner_id.id,
			quantity=vals.get('product_uom_qty') or self.product_uom_qty,
			date=self.order_id.date_order,
			pricelist=self.order_id.pricelist_id.id,
			uom=self.product_uom.id
		)

		result = {'domain': domain}

		title = False
		message = False
		warning = {}
		if product.sale_line_warn != 'no-message':
			title = _("Warning for %s") % product.name
			message = product.sale_line_warn_msg
			warning['title'] = title
			warning['message'] = message
			result = {'warning': warning}
			if product.sale_line_warn == 'block':
				self.product_id = False
				return result

		name = product.name_get()[0][1]
		if product.description_sale:
			name += '\n' + product.description_sale
		vals['name'] = name

		self._compute_tax_id()

		if self.order_id.pricelist_id and self.order_id.partner_id:
			vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
		self.update(vals)

		return result

	@api.onchange('product_uom', 'product_uom_qty')
	def product_uom_change(self):
		if not self.product_uom or not self.product_id:
			self.price_unit = 0.0
			return
		if self.order_id.pricelist_id and self.order_id.partner_id:
			product = self.product_id.with_context(
				lang=self.order_id.partner_id.lang,
				partner=self.order_id.partner_id.id,
				quantity=self.product_uom_qty,
				date=self.order_id.date_order,
				pricelist=self.order_id.pricelist_id.id,
				uom=self.product_uom.id,
				fiscal_position=self.env.context.get('fiscal_position')
			)
			self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

	@api.multi
	def name_get(self):
		if self._context.get('sale_show_order_product_name'):
			result = []
			for so_line in self:
				name = '%s - %s' % (so_line.order_id.name, so_line.product_id.name)
				result.append((so_line.id, name))
			return result
		return super(StockoutOrderLine, self).name_get()

	@api.model
	def name_search(self, name='', args=None, operator='ilike', limit=100):
		if self._context.get('sale_show_order_product_name'):
			if operator in ('ilike', 'like', '=', '=like', '=ilike'):
				domain = expression.AND([
					args or [],
					['|', ('order_id.name', operator, name), ('product_id.name', operator, name)]
				])
				return self.search(domain, limit=limit).name_get()
		return super(StockoutOrderLine, self).name_search(name, args, operator, limit)

	@api.multi
	def unlink(self):
		if self.filtered(lambda x: x.state in ('confirm')):
			raise UserError(_('You can not remove a stockout order line.\nDiscard changes and try setting the quantity to 0.'))
		return super(StockoutOrderLine, self).unlink()