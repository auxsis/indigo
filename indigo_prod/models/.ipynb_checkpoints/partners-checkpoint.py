

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import datetime
import time

import logging
_logger = logging.getLogger(__name__)


class Partners(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _get_invoice_count(self):
        for record in self:
            invoice_count = len(record.invoice_ids)
            record.invoice_count = invoice_count

    partner_area_id = fields.Many2one(
        'indigo_prod.partner_area',
        string='Partner Area',
    )

    primary_contact_person = fields.Char(
        string='Contact Person',
    )
    
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoice_count')
    
    @api.model
    def get_partners_in_customer_statement_list(self, invoice_ids=False):
        company_id = self.env.user.company_id
        context = self.env.context
        cr = self.env.cr
        date = 'date' in context and context['date'] or time.strftime('%Y-%m-%d')

        cr.execute(
            "SELECT l.partner_id, l.followup_line_id, l.date_maturity, l.date, l.id, fl.delay, l.invoice_id "\
            "FROM account_move_line AS l "\
                "LEFT JOIN account_account AS a "\
                "ON (l.account_id=a.id) "\
                "LEFT JOIN account_account_type AS act "\
                "ON (a.user_type_id=act.id) "\
                "LEFT JOIN account_followup_followup_line AS fl "\
                "ON (l.followup_line_id=fl.id) "\
            "WHERE (l.reconciled IS FALSE) "\
                "AND (act.type='receivable') "\
                "AND (l.partner_id is NOT NULL) "\
                "AND (a.deprecated='f') "\
                "AND (l.debit > 0) "\
                "AND (l.company_id = %s) " \
                "AND (l.blocked IS FALSE) " \
            "ORDER BY l.date", (company_id.id,))  #l.blocked added to take litigation into account and it is not necessary to change follow-up level of account move lines without debit
        move_lines = cr.fetchall()
        old = None
        fups = {}
        fup_id = 'followup_id' in context and context['followup_id'] or self.env['account_followup.followup'].search([('company_id', '=', company_id.id)]).id
        if not fup_id:
            raise Warning(_('No follow-up is defined for the company "%s".\n Please define one.') % company_id.name)

        if not fup_id:
            return {}

        current_date = datetime.date(*time.strptime(date, '%Y-%m-%d')[:3])
        cr.execute(
            "SELECT * "\
            "FROM account_followup_followup_line "\
            "WHERE followup_id=%s "\
            "ORDER BY delay", (fup_id,))

        #Create dictionary of tuples where first element is the date to compare with the due date and second element is the id of the next level
        for result in cr.dictfetchall():
            delay = datetime.timedelta(days=result['delay'])
            fups[old] = (current_date - delay, result['id'])
            old = result['id']

        fups[old] = (current_date - delay, old)

        result = {}

        partners_to_skip = self.env['res.partner'].search([('payment_next_action_date', '>', date)])

        #Fill dictionary of accountmovelines to_update with the partners that need to be updated
        for partner_id, followup_line_id, date_maturity, date, id, delay, invoice_id in move_lines:
            if invoice_id in invoice_ids:
                if not partner_id or partner_id in partners_to_skip.ids:
                    continue
                if followup_line_id not in fups:
                    continue
                if date_maturity:
                    if date_maturity <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                        if partner_id not in result:
                            result.update({partner_id: (fups[followup_line_id][1], delay)})
                        elif result[partner_id][1] < delay:
                            result[partner_id] = (fups[followup_line_id][1], delay)
                elif date and date <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                    if partner_id not in result:
                        result.update({partner_id: (fups[followup_line_id][1], delay)})
                    elif result[partner_id][1] < delay:
                        result[partner_id] = (fups[followup_line_id][1], delay)
        return result


class PartnerArea(models.Model):
    _name = 'indigo_prod.partner_area'

    name = fields.Char(
        string='Partner Area',
        required=True
    )


class IndigoSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_quantity = fields.Float(
        string='Available Quantity',
        compute="_value_available_quantity"
    )

    product_model = fields.Char(
        string='Model',
        compute="_value_available_quantity"
    )

    @api.multi
    @api.onchange('product_id', 'product_uom_qty')
    def _value_available_quantity(self):
        for rec in self:
            rec.product_model = rec.product_id.carmodel_id.name
            rec.available_quantity = rec.product_id.virtual_available

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id_indigo(self):
        if (self.product_id and self.order_id.partner_id):
            previous_orders = self.env['sale.order.line'].search([("order_id.partner_id", "=", self.order_id.partner_id.id),
                                                                  ("product_id", "=", self.product_id.id)], order="id desc", limit=5)

            message = ""
            for rec in previous_orders:
                message = (message + "Sales Order #:" + rec.order_id.name + " Order Date:" + str(rec.order_id.date_order)
                           + '\n' + " Quantity:" + str(rec.product_uom_qty)
                           + " Unit Price:" + str(rec.price_unit) + " Discount:" + str(
                               rec.discount) + " Subtotal:" + str(rec.price_subtotal) + '\n'
                           + '\n')
                _logger.info(rec.order_id.name)

            if (message):
                warning = {}
                title = "Previous quotations for this customer and product"
                warning = {
                    'title': title,
                    'message': message,
                }
                return {'warning': warning}
