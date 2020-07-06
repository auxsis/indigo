# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'
    _description = 'Res Config Settings'

    default_vendor_id = fields.Many2one('res.partner', 'Default Vendor', domain=[('supplier','=',True)])

    @api.model
    def get_values(self):

        res = super(ResConfigSettings, self).get_values()
        res.update(
            default_vendor_id=int(self.env['ir.config_parameter'].sudo().get_param(
                'jt_picking_batch_bill.default_vendor_id')))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        partner_id = self.default_vendor_id
        param.set_param('jt_picking_batch_bill.default_vendor_id', partner_id.id)


