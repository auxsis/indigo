# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

from odoo.tools.misc import formatLang

class ProductUpdater(models.Model):
    _name = 'product.updater'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product"

    @api.model
    def _default_user(self):
        return self.env.context.get('responsible', self.env.user.id)

    name = fields.Char('Name', required=True, track_visibility='onchange')
    date = fields.Date('Date', default=fields.Datetime.now, track_visibility='onchange',)
    responsible = fields.Many2one('res.users','Responsible', default=_default_user, readonly="True", track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated')], string='State', default='draft')
    lines = fields.One2many('product.updater.line','product_updater_id','Lines', track_visibility='onchange')

    @api.multi
    def action_validate(self):
        msg = ''
        for record in self.lines:
            flag = False
            rec_msg = ''
            if record.cost != record.product_id.standard_price:
                flag = True
                rec_msg += '<li><b>Cost: </b> ' + str(record.cost) + \
                ' <b> from </b> ' + str(record.product_id.standard_price) + '</li>'
            if record.sale_price != record.product_id.list_price:
                flag = True
                rec_msg += '<li><b>Sales Price: </b> ' + str(record.sale_price) + \
                ' <b> from </b> ' + str(record.product_id.list_price) + '</li>'
            if flag:
                msg += '<ul><b>========' +record.product_id.name+ '========</b>' + rec_msg + '</ul>'
            record.product_id.write({'standard_price':record.cost,'list_price':record.sale_price})
        self.message_post(body=msg)
        self.write({'state':'validated'})

class ProductUpdaterLine(models.Model):
    _name = 'product.updater.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Updater Line"

    product_updater_id = fields.Many2one('product.updater','Product Updater')
    product_id = fields.Many2one('product.product','Product', required=True, track_visibility='onchange')
    cost = fields.Float('Cost', required=True, track_visibility='onchange')
    sale_price = fields.Float('Sale Price', required=True, track_visibility='onchange')

    @api.onchange('product_id')
    def product_onchange(self):
        if self.product_id:
            self.cost = self.product_id.standard_price
            self.sale_price = self.product_id.list_price