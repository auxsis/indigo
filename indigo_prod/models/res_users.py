# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.tools import partition, collections, lazy_property

_logger = logging.getLogger(__name__)


class IbasResUser(models.Model):

    _inherit = 'res.users'

    journal_ids = fields.Many2many(
        'account.journal', 'user_journal_rel', 'user_id', 'journal_id', string="Journal")

    def write(self, values):
        values = self._remove_reified_groups(values)
        res = super(IbasResUser, self).write(values)
        group_multi_journal = self.env.ref(
            'indigo_prod.group_multi_journal', False)
        if group_multi_journal and 'journal_ids' in values:
            self.write({'groups_id': [(3, group_multi_journal.id)]})
            for user in self:
                if len(user.journal_ids) <= 0 and user.id in group_multi_journal.users.ids:
                    user.write({'groups_id': [(4, group_multi_journal.id)]})
                elif len(user.journal_ids) >= 1 and user.id not in group_multi_journal.users.ids:
                    user.write({'groups_id': [(4, group_multi_journal.id)]})
        return res
