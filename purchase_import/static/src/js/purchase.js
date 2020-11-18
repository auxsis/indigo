odoo.define('purchase_import.tree_import_button', function (require) {
    "use strict";

    const core = require('web.core');
    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    const viewRegistry = require('web.view_registry');

    const QWeb = core.qweb;

    const PurchaseListController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the payslip list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("PurchaseListView.purchase_import_wizard", this)));
            const self = this;
            this.$buttons.on('click', '.btn_purchase_import_wizard', function () {
                return self._rpc({
                    model: 'purchase.order.import',
                    method: 'action_import_purchase_order',
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });

    const PurchaseListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: PurchaseListController,
        }),
    });

    viewRegistry.add('purchase_import_tree', PurchaseListView);
});
