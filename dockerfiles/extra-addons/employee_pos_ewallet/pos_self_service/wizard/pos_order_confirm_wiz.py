# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-TODAY Acespritech Solutions Pvt Ltd
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp import tools
from openerp.tools import float_is_zero
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)
from openerp.exceptions import ValidationError,Warning
from lxml import etree
import time
from openerp.osv import osv
from openerp import SUPERUSER_ID


class pos_order(models.Model):
    _name = 'pos.order.confirm'

    """ Add new class for confirmation of pos order """

    name = fields.Char('Order Ref')
    # student_id = fields.Many2one("op.student", "Student")
    employee_id = fields.Many2one("hr.employee", "Employee")
    session_id = fields.Many2one('pos.session', 'Session')
    date_order = fields.Datetime('Order Date')
    amount = fields.Float('Amount')
    partner_id = fields.Many2one('res.partner', 'Customer')
    order_id = fields.Many2one('pos.order', 'Order Id')
    confirm_lines = fields.One2many('pos.order.line.confirm', 'confirm_order_id', 'Lines')
    amount_total = fields.Float('Total')
    amount_tax = fields.Float('Tax')
    stock_location_id = fields.Many2one('stock.location', string="Shop", domain=[('usage', '=', 'internal')],required=True)

    @api.multi
    def order_confirm(self):
        if self.order_id:
            for line in self.order_id.lines:
                if line.qty == 0:
                    line.sudo().unlink()
            self.order_id.sudo().copy_check()



class pos_order(models.Model):
    _name = 'pos.order.line.confirm'

    image = fields.Binary('Image')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Integer('Purchase Qty')
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Float('Subtotal w/o Tax')
    price_subtotal_incl = fields.Float('Subtotal')
    confirm_order_id = fields.Many2one('pos.order.confirm', 'Confirm Lines')

