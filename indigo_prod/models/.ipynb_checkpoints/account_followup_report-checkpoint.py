from odoo import models, fields, api, _

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