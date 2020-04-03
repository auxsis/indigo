/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.dashboard', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var PettyCashDashboardView = Widget.extend(ControlPanelMixin, {
//	template: 'itm_petty_cash.dashboard',
	events: _.extend({}, Widget.prototype.events, {
		'click .cash_received': 'cash_received',
        'click .balance': 'action_balance',
        'click .request': 'action_request',
        'click .requested': 'request_money',
        'click .requested_reconcile': 'request_reconcile',
        'click .account_expense_details_top1': 'action_account_expense_details_top1',
        'click .account_expense_details_top2': 'action_account_expense_details_top2',
        'click .account_expense_details_top3': 'action_account_expense_details_top3',
        'click .account_expense_details_top4': 'action_account_expense_details_top4',
        'click .account_expense_details_top5': 'action_account_expense_details_top5',
        'click .current_year': 'action_current_year',
        'click .last_year': 'action_last_year',
        'click .current_year_quarter': 'action_current_year_quarter',
        'click .last_year_quarter': 'action_last_year_quarter',
        'click .expense': 'action_expense',
        'click .my_profile': 'action_my_profile',
        'click #generate_petty_cash_pdf': function(){this.generate_petty_cash_pdf("bar");},
        'click #generate_custodian_pdf': function(){this.generate_petty_cash_pdf("pie")},
	}),
	init: function(parent, context) {
        this._super(parent, context);
        var employee_data = [];
        var self = this;
        if (context.tag == 'itm_petty_cash.dashboard') {
            self._rpc({
                model: 'petty.cash.dashboard',
                method: 'get_petty_cash_info',
            }, []).then(function(result){
                self.employee_data = result[0]
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var hr_dashboard = QWeb.render( 'itm_petty_cash.dashboard', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(hr_dashboard).prependTo(self.$el);
        self.graph();
        self.previewTable();
        return hr_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },
    cash_received: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Cash Received"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                'search_default_requested_employee_id': [self.employee_data.id],
                'default_requested_employee_id': self.employee_data.id,
                },
            domain: [['state','=', 'cash_dispatch']],
            search_view_id: self.employee_data.cash_search_view_id,
            target: 'current'
        })
    },
    request_money: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Petty Cash Request"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_employee_id': [self.employee_data.id],
                    'default_employee_id': self.employee_data.id,
                    },
            target: 'current',
             domain: [['state','in', ['request']]],
        })
    },
    action_balance: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Petty Cash Balance"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_requested_employee_id': [self.employee_data.id],
                    'default_requested_employee_id': self.employee_data.id,
                    },
            target: 'current'
        })
    },
    action_request: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Petty Cash to Request"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_requested_employee_id': [self.employee_data.id],
                    'default_requested_employee_id': self.employee_data.id,
                    },
            target: 'current',
            domain: [['state','in', ['draft','request']]],
        })
    },
    request_reconcile: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Petty Reconcile Request"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_employee_id': [self.employee_data.id],
                    'default_employee_id': self.employee_data.id,
                    },
            target: 'current',
             domain: [['state','in', ['to_reconcile']]],
        })
    },
    action_account_expense_details_top1: function(event) {
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Account Expenses Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['id','in', self.employee_data.expenses_line_ids],['account_expense_id','=',self.employee_data.account_filter_top1],],
            search_view_id: self.employee_data.cash_search_view_id,
            target: 'current'
        })
    },
    action_account_expense_details_top2: function(event) {
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Account Expenses Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['id','in', self.employee_data.expenses_line_ids],['account_expense_id','=',self.employee_data.account_filter_top2],],
            search_view_id: self.employee_data.cash_search_view_id,
            target: 'current'
        })
    },
    action_account_expense_details_top3: function(event) {
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Account Expenses Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['id','in', self.employee_data.expenses_line_ids],['account_expense_id','=',self.employee_data.account_filter_top3],],
            search_view_id: self.employee_data.cash_search_view_id,
            target: 'current'
        })
    },
    action_account_expense_details_top4: function(event) {
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Account Expenses Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['id','in', self.employee_data.expenses_line_ids],['account_expense_id','=',self.employee_data.account_filter_top4],],
            search_view_id: self.employee_data.cash_search_view_id,
            target: 'current'
        })
    },
    action_account_expense_details_top5: function(event) {
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Account Expenses Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            views: [['id','in', self.employee_data.expenses_line_ids],[false, 'list'],[false, 'graph'],],
            domain: [['account_expense_id','=',self.employee_data.account_filter_top5],],
            search_view_id: self.employee_data.cash_search_view_id,
            target: 'current'
        })
    },
    action_current_year: function(event){
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Current Year Petty Cash Expense Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['state','=','paid'],],
            search_view_id: self.employee_data.petty_cash_line_view_id,
            target: 'current',
            context: {
                'search_default_current_date_maturity': true,
                'default_current_date_maturity': true,
                },
        })
    },
    
    action_last_year: function(event){
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Last Year Petty Cash Expense Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['state','=','paid'],],
            search_view_id: self.employee_data.petty_cash_line_view_id,
            target: 'current',
            context: {
                'search_default_last_date_maturity': true,
                'default_last_date_maturity': true,
                },
        })
    },
    action_current_year_quarter: function(event){
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Current Quarter Petty Cash Expense Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['state','=','paid'],],
            search_view_id: self.employee_data.petty_cash_line_view_id,
            target: 'current',
            context: {
                'search_default_current_quater_date_maturity': true,
                'default_current_quater_date_maturity': true,
                },
        })
    },
    action_last_year_quarter: function(event){
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Last Quarter Petty Cash Expense Details"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash.line',
            view_mode: 'tree,form',
            view_type: 'tree',
            views: [[false, 'list'],[false, 'form'],],
            domain: [['state','=','paid'],],
            search_view_id: self.employee_data.petty_cash_line_view_id,
            target: 'current',
            context: {
                'search_default_last_quarter_date_maturity': true,
                'default_last_quarter_date_maturity': true,
                },
        })
    },    
    action_expense: function(event){
    	var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Petty Cash Balance"),
            type: 'ir.actions.act_window',
            res_model: 'petty.cash',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_requested_employee_id': [self.employee_data.id],
                    'default_requested_employee_id': self.employee_data.id,
                    },
            target: 'current'
        })
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
 // Here we are plotting bar,pie chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#myChart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                // "October", "November", "December"],
                labels: self.employee_data.petty_cash_label,
                datasets: [{
                    label: 'Expenses',
                    data: self.employee_data.petty_cash_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.employee_data.petty_cash_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.employee_data.
                            petty_cash_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                             /self.employee_data.petty_cash_dataset.length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
        //Pie Chart
        var piectx = this.$el.find('#custodianChart');
        bg_color_list = []
        for (var i=0;i<=self.employee_data.custodian_dataset.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.employee_data.custodian_dataset,
                    backgroundColor: bg_color_list,
                    label: 'Custodian Pie'
                }],
                labels:self.employee_data.custodian_labels,
            },
            options: {
                responsive: true
            }
        });
    },
    action_my_profile: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("My Profile"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: self.employee_data.id,
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            context: {},
            domain: [],
            target: 'inline'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    generate_petty_cash_pdf: function(chart){
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChart');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#custodianChart');
        }

        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('report.pdf');
    },
    previewTable: function() {
    	$('#expenses_details').DataTable( {
        	dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Expenses Details',
                    text: 'PDF',
//                    exportOptions: {
//                        modifier: {
//                            selected: true
//                        }
//                    }
                },
                {
                    extend: 'print',
                    exportOptions: {
                    columns: ':visible'
                    }
                },
            'colvis'
            ],
            columnDefs: [ {
             //   targets: -1,
                visible: false
            } ],
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            pageLength: 15,
        } );
    },

});
core.action_registry.add('itm_petty_cash.dashboard', PettyCashDashboardView);
return PettyCashDashboardView
});
