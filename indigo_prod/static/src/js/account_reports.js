odoo.define('account_report.tour', function (require) {
    'use strict';
    
    var accountReportsWidget = require('account_reports.account_report');
    
    accountReportsWidget.include({
        render_searchview_buttons: function() {
            var self = this;
            
            this.$searchview_buttons.find('.js_customer_statement_partner_auto_complete').select2();
//             if (self.report_options.analytic) {
            self.$searchview_buttons.find('[data-filter="account_partners"]').select2("val", self.report_options.account_partners);
//             }
            this.$searchview_buttons.find('.js_customer_statement_partner_auto_complete').on('change', function(){
                self.report_options.account_partners = self.$searchview_buttons.find('[data-filter="account_partners"]').val();
                return self.reload().then(function(){
                    self.$searchview_buttons.find('.customer_statement_partner_filter').click();
                })
            });
            
            this._super.apply(this, arguments);
        },
    });
    
});