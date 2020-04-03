# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _

class account_cheque_template(models.AbstractModel):
    _name = 'report.bi_account_cheque.account_cheque_template'


    @api.multi
    def get_report_values(self, docids, data=None):
            record_ids = self.env[data['model']].browse(data['form'])
            #in_record_ids = self.env['account.check'].browse(data['in_data'])
            #out_record_ids = self.env['account.check'].browse(data['out_data'])
            val = {
                                 'doc_ids': docids,
                                 'doc_model': 'account.cheque',
                                 'docs': record_ids,
                                 #'in_docs': in_record_ids,
                                 #'out_docs' : out_record_ids,
                                 'data' : data,
                                 }
            return val

    '''@api.model
        def get_report_values(self, docids, data=None):
                print ("---------data-----------",data)
                in_record_ids = self.env[data['model']].browse(data['in_data'])
                out_record_ids = self.env[data['model']].browse(data['out_data'])
                val = {
                                     'doc_ids': docids,
                                     'doc_model': 'account.check',
                                     'in_docs': in_record_ids,
                                     'out_docs' : out_record_ids,
                                     'data' : data,
                                     }
                print (";;;;;;;;;;;vallllllllllll",val)
                return val  '''      
                                     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
