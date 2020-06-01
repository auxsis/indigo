from odoo import models, fields, api, _
from datetime import datetime
from odoo.addons import decimal_precision as dp


class IndigoProductsMain(models.Model):
    _inherit = 'product.product'

    qty_at_date = fields.Float('Quantity', compute='_compute_stock_value',
                               default=0.0, digits=dp.get_precision('Product Unit of Measure'), store=True)

    stock_value = fields.Float(
        'Value', compute='_compute_stock_value', store=True)


class IndigoProducts(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('carmodel_group')
    def _compute_carmodel_group_id(self):
        for record in self:
            record.carmodel_group_id = record.carmodel_group and record.carmodel_group[
                0] or False

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
        store=True,
        compute="_computed_local_cost",
        groups="base.group_erp_manager"
    )

    tags_ids = fields.Many2many(
        'indigo_prod.vehicle_tags',
        string='Vehicle Tags',
    )

    fit = fields.Selection(
        [('one', 'One Fit'), ('multiple', 'Multiple Fit'), ])

    cartype_id = fields.Many2one('indigo_prod.cartype', string='Car Type')
    factory_id = fields.Many2one('indigo_prod.factory', string='Factory')
    country_id = fields.Many2one('res.country', string='Country')

    carmodel_group = fields.Many2many(
        'indigo_prod.carmodelgroup', string='Car Model Group')
    carmodel_group_id = fields.Many2one(
        'indigo_prod.carmodelgroup', string='Car Model Group ID', compute="_compute_carmodel_group_id", store=True)

    # carmodel_group1_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group', compute="_compute_carmodel_group1_id", store=True)
    # carmodel_group2_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group 2')
    # carmodel_group3_id = fields.Many2one('indigo_prod.carmodelgroup', string='Car Model Group 3')

    floor_location = fields.Char()
    rack_location = fields.Char()

    carmodel_group = fields.Many2many(
        'indigo_prod.carmodelgroup', string='Car Model Group')
    carmodel_year = fields.Integer(related='carmodel_id.year', string='Year')

    value = fields.Float(compute='_compute_value', string='value')
    most_recent = fields.Date(
        compute='_compute_most_recent', string='Most Recent Reception Date')
    qty_received = fields.Float(
        compute='_compute_most_recent', string='Qty Received During Recent Reception Date')
    #stock_ml_ids = fields.Many2one('stock.move.line')

    @api.depends('type')
    def _compute_most_recent(self):
        for rec in self:
            # move = self.env['stock.move.line'].search([('state', '=', 'done'), ('product_id', '=', rec.id)])[-1]
            # move = self.env['stock.move.line'].search([('state', '=', 'done'), ('product_id', '=', rec.id)])
            product_ids = rec.with_context(active_test=False).product_variant_ids.ids
            move_lines = self.env['stock.move.line'].search([('state', '=', 'done'), ('product_id', 'in', product_ids)], order='id desc')
            move_id = False
            most_recent = False
            qty_received = 0
            for move in move_lines:
                if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':
                    if not move_id:
                        move_id = move
            if move_id:
                most_recent = move_id.date
                qty_received = move_id.qty_done
            rec.most_recent = most_recent
            rec.qty_received = qty_received

    @api.depends('standard_price', 'qty_available')
    def _compute_value(self):
        for rec in self:
            rec.value = self.standard_price * self.qty_available

    @api.depends('foreign_cost', 'exchange_rate')
    def _computed_local_cost(self):
        for record in self:
            record.local_cost = record.foreign_cost * record.exchange_rate
            record.standard_price = record.local_cost

    @api.onchange('factory_id')
    def get_country(self):
        self.country_id = self.factory_id.country_id
        
    @api.multi
    def action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('indigo_prod.action_product_sale_order_list')
        product_ids = self.with_context(active_test=False).product_variant_ids.ids
        
        sale_line = self.env['sale.order.line'].search([('product_id','in',product_ids),('state', 'in', ['sale', 'done'])])
        sale_ids = sale_line.mapped('order_id').ids

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            # 'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('id', 'in', sale_ids)],
        }


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
