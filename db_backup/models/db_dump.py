# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import os


class DatabaseBackup(models.Model):
    _name = 'database.backup'
    _description = 'Database Backup'

    name = fields.Char('name', readonly=True)

    def dump_db(self):
        db_name = self.env['ir.config_parameter'].search(
            [('key', '=', 'db_backup.db_name_config')]).value.strip()
        path = self.env['ir.config_parameter'].search(
            [('key', '=', 'db_backup.path_config')]).value.strip()
        path = path if path else '/home'

        db_path = path + '/' + db_name + '_' + datetime.now().strftime("%Y%m%d")
        if os.path.exists(db_path):
            os.remove(db_path)
        os.system("pg_dump {} > {}".format(db_name, db_path))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    db_name_config = fields.Text(string='Database Name', help='Database name you want to backup.')
    path_config = fields.Text(string='Path', help='Where you want to dump database.')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            db_name_config=self.env['ir.config_parameter'].sudo().get_param(
                'db_backup.db_name_config'),
            path_config=self.env['ir.config_parameter'].sudo().get_param(
                'db_backup.path_config'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('db_backup.db_name_config',
                                                         self.db_name_config)
        self.env['ir.config_parameter'].sudo().set_param('db_backup.path_config',
                                                         self.path_config)