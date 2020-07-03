from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools.misc import formatLang, format_date, ustr

import logging
_logger = logging.getLogger(__name__)

class AccountReportFollowupAll(models.AbstractModel):
    _inherit = "account.followup.report.all"
    
    def get_templates(self):
        templates = super(AccountReportFollowupAll, self).get_templates()
        templates['search_template'] = 'indigo_prod.followup_search_template_custom'
        return templates
    
#     def compute_pages(self, options):
#         partner_in_need_of_action = self.get_partners_in_need_of_action(options)
#         partner_in_need_of_action = partner_in_need_of_action.sorted(key=lambda x: x.name or '')
#         skipped_partners = self.env['res.partner'].browse(options.get('skipped_partners'))
#         total_partners_to_do = (partner_in_need_of_action - skipped_partners).ids
#         options['total_pager'] = int(1+ (len(total_partners_to_do)/self.PAGER_SIZE))
#         max_index = min(len(total_partners_to_do), options['pager']*self.PAGER_SIZE)
#         if options.get('pager') > (options['total_pager']):
#             options['pager'] = options['total_pager']
#         options['partners_to_show'] = total_partners_to_do[(options['pager']-1)*self.PAGER_SIZE:max_index]
#         options['progressbar'][1] = len(total_partners_to_do)
#         options['progressbar'][2] = int(100 * options['progressbar'][0] / (options['progressbar'][1] or 1))
#         return options

#     def get_options(self, previous_options):
#         options = super(AccountReportFollowupAll, self).get_options(previous_options)
#         options = self.compute_pages(options)
#         return options

    @api.multi
    def get_report_informations(self, options):
        informations = super(AccountReportFollowupAll, self).get_report_informations(options)
        options = informations['options']
        searchview_dict = {'options': options, 'context': self.env.context}
        searchview_dict['account_partners'] = [(t.id, t.name) for t in self.env['res.partner'].search([('customer','=',True)])] or False
        informations['searchview_html'] = self.env['ir.ui.view'].render_template(self.get_templates().get('followup_search_template_custom', 'indigo_prod.followup_search_template_custom'), values=searchview_dict)
        return informations
    
class AccountReportFollowup(models.AbstractModel):
    _inherit = "account.followup.report"
    
    def get_lines(self, options, line_id=None):
        invoice_ids = self._context.get('invoice_ids', [])
        
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []
        lang_code = partner.lang or self.env.user.lang or 'en_US'

        lines = []
        res = {}
        today = datetime.today().strftime('%Y-%m-%d')
        line_num = 0
        for l in partner.unreconciled_aml_ids:
            if self.env.context.get('print_mode') and l.blocked:
                continue
            # FILTER ENTRIES FROM CHEQUE
            if "CHK" in l.move_id.name:
                continue
            # FILTER ENTRIES FROM CUSTOMER STATEMENT LIST
            if invoice_ids and l.invoice_id.id not in invoice_ids:
                continue
            currency = l.currency_id or l.company_id.currency_id
            if currency not in res:
                res[currency] = []
            res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            aml_recs = sorted(aml_recs, key=lambda aml: aml.blocked)
            for aml in aml_recs:
                amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date'}
                if is_payment:
                    date_due = ''
                amount = formatLang(self.env, amount, currency_obj=currency)
                amount = amount.replace(' ', '&nbsp;') if self.env.context.get('mail') else amount
                line_num += 1
                columns = [format_date(self.env, aml.date, lang_code=lang_code), date_due, aml.invoice_id.name or aml.name, aml.expected_pay_date and aml.expected_pay_date +' '+ aml.internal_note or '', {'name': aml.blocked, 'blocked': aml.blocked}, amount]
                if self.env.context.get('print_mode'):
                    columns = columns[:3]+columns[5:]
                lines.append({
                    'id': aml.id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
            totalXXX = formatLang(self.env, total, currency_obj=currency)
            totalXXX = totalXXX.replace(' ', '&nbsp;') if self.env.context.get('mail') else totalXXX
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'unfoldable': False,
                'level': 0,
                'columns': [{'name': v} for v in ['']*(2 if self.env.context.get('print_mode') else 4) + [total >= 0 and _('Total Due') or '', totalXXX]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                total_issued = total_issued.replace(' ', '&nbsp;') if self.env.context.get('mail') else total_issued
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 0,
                    'columns': [{'name': v} for v in ['']*(2 if self.env.context.get('print_mode') else 4) + [_('Total Overdue'), total_issued]],
                })
                
        return lines