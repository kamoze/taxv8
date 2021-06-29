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


class pos_config(models.Model):
    _inherit = 'pos.config'

    interface = fields.Selection([('normal', 'Normal'),
                                  ('self', 'Self Service')],
                                 string='POS Interface', default='normal')
    self_journal_id = fields.Many2one('account.journal', string="Self Service Journal")
    no_of_receipt_print = fields.Integer("No. Of Receipt Print")
    expiration_period = fields.Selection([('days', 'Days'), ('hours', 'Hours')], string="Expiration period", default='days')
    time_period = fields.Integer("Time Period")

    show_qty = fields.Boolean(string='Display Stock')
    restrict_order = fields.Boolean(string='Restrict Order When Out Of Stock')
    prod_qty_limit = fields.Integer(string="Restrict When Product Qty Remains")
    custom_msg = fields.Char(string="Custom Message")

class pos_make_payment(models.Model):
    _inherit = 'pos.make.payment'

    def check(self, cr, uid, ids, context=None):
        res = super(pos_make_payment, self).check(cr, uid, ids, context)
        context = context or {}
        uid = SUPERUSER_ID
        order_obj = self.pool.get('pos.order')
        active_id = context and context.get('active_id', False)
        order = order_obj.browse(cr, uid, active_id, context=context)
        if context.get('employee_id'):
            emp_id = self.pool.get('hr.employee').browse(cr, uid, context.get('employee_id'), context=context)
            if emp_id.available_balance >= order.amount_total:
                self.pool['employee.expenses'].create(cr, uid, {
                    'name': emp_id.id,
                    'source': order.name,
                    'amount': order.amount_total
                })
            else:
                raise ValidationError(_('Sorry, You have not sufficient amount.'))
        return res

class pos_order(models.Model):
    _inherit = 'pos.order'

    picking_ids = fields.Many2many(
        "stock.picking",
        string="Multiple Picking",
        copy=False)

    # student_id = fields.Many2one("op.student", "Student")
    employee_id = fields.Many2one("hr.employee", "Employee")
    receipt_count = fields.Integer("Receipt Counter")
    is_self_service = fields.Boolean("Is Self Service")
    is_from_pos = fields.Boolean("Is From POS")
    amount = fields.Float("Balance")
    stock_location_id = fields.Many2one('stock.location', string="Stock Location", domain=[('usage', '=', 'internal')], readonly=True)
#     currency_id = fields.Many2one('res.currency', 'Currency', required=True)


    ## GEO: customization

    @api.multi
    def confirm_pos_order(self):
        view_id = self.env['ir.model.data'].get_object_reference('employee_pos_ewallet', 'geo_pos_confirmation_form_view')[1]
        product_list = []



        ## get all product list and append to pos order lines

        if self.lines:
            flag=False
            for line in self.lines:
                if line.qty > 0.00:
                    flag=True
                    product_vals = {
                        'image': line.product_id.image_medium,
                        'product_id': line.product_id.id,
                        'price_unit': line.product_id.lst_price,
                        'qty': line.qty,
                        'price_subtotal': line.price_subtotal,
                        'price_subtotal_incl': line.price_subtotal_incl,
                    }
                    product_list.append(product_vals)
            if not flag:
                raise Warning(_("Please enter product quantity to place order."))
            return {
                'type': 'ir.actions.act_window',
                'name': _('POS Order Confirmation'),
                'res_model': 'pos.order.confirm',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'context': {
                    'default_name': self.name,
                    'default_date_order': self.date_order,
                    'default_session_id': self.session_id.id,
                    'default_partner_id': self.partner_id.id,
                    'default_amount': self.amount,
                    # 'default_sale_journal': self.sale_journal.id,
                    'default_confirm_lines': product_list,
                    'default_amount_total': self.amount_total,
                    'default_amount_tax': self.amount_tax,
                    # 'default_student_id': self.student_id.id,
                    'default_employee_id': self.employee_id.id,
                    'default_order_id':self.id,
                    'default_stock_location_id':self.stock_location_id.id,
                },
                'target': 'new',
            }


    @api.multi
    def open_confirm_popup(self):
        if self and self.lines:
            ctx = self._context.copy()
            ctx.update({'default_order_id':self.id})
            view_id = self.env['ir.model.data'].get_object_reference('employee_pos_ewallet', 'pos_self_service_confirmation_wizard')[1]
            return {
                'type': 'ir.actions.act_window',
                'name': _('Confirmation'),
                'res_model': 'pos.order.confirm.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'new',
                'context':ctx
            }
        else:
            raise Warning(_("Please add products."))

    def _get_default_amount(self, cr, uid, context=None):
        context = context or {}
        amount = 0
        if context.get('default_employee_id'):
            emp_id = self.pool.get('hr.employee').browse(cr, uid, context.get('default_employee_id'), context=context)
            return emp_id.available_balance
        return False

    def _get_default_partner(self, cr, uid, context=None):
        context = context or {}
        # if context.get('default_student_id'):
        #     student_id = self.pool.get('op.student').browse(cr, uid, context.get('default_student_id'), context=context)
        #     return student_id.partner_id.id
        if context.get('default_employee_id'):
            emp_id = self.pool.get('hr.employee').browse(cr, uid, context.get('default_employee_id'), context=context)
            return emp_id.user_id.partner_id.id
        return False

    _defaults = {
        'amount': _get_default_amount,
        'partner_id':_get_default_partner,
    }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(pos_order, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

        my_group_gid = self.env.ref(
            'employee_pos_ewallet.aces_group_self_service').id
        user_group_ids = self.env['res.users'].browse(self._uid).groups_id.ids
        doc = etree.XML(res['arch'])
        emp_grp_id = self.env.ref('base.group_user').id
        if emp_grp_id in user_group_ids:
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='POS Orders']")
                for node in nodes:
                    node.set('create', '0')
            if view_type == 'form':
                for node in doc.xpath("//form[@string='Point of Sale Orders']"):
                    node.set('create', '0')
                    node.set('edit', '0')

        portal_grp_id = self.env.ref('base.group_portal').id
        if portal_grp_id in user_group_ids:
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='POS Orders']")
                for node in nodes:
                    node.set('create', '0')
            if view_type == 'form':
                for node in doc.xpath("//form[@string='Point of Sale Orders']"):
                    node.set('create', '0')
                    node.set('edit', '0')

        if my_group_gid in user_group_ids:
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='POS Orders']")
                for node in nodes:
                    node.set('create', '0')
            if view_type == 'form':
                for node in doc.xpath("//form[@string='Point of Sale Orders']"):
                    node.set('create', '0')
                    node.set('edit', '0')
                for node in doc.xpath("//button[@name='open_confirm_popup']"):
                    node.set('invisible', '1')
        res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('session_id')
    def onchange_session_id(self):
        self.pricelist_id = self.session_id.config_id.pricelist_id.id

    @api.multi
    def copy_check(self, context=None):
        context = self._context or {}
        order_obj = self.pool.get('pos.order')
        order = self.id
        amount = self.amount_total - self.amount_paid

        data = self.read()[0]
        data['amount'] = amount
        # this is probably a problem of osv_memory as it's not compatible with normal OSV's
        if self.session_id:
            if context.get('active_model') == 'pos.self.service.wizard':
                account_journal = self.env['pos.session'].browse(context.get('pos_session_id')).config_id.self_journal_id
                if account_journal and account_journal.id:
                    data['journal'] = account_journal.id
            else:
                for journal in self.session_id.config_id.journal_ids:
                        data['journal'] = journal.id
        if context.get('employee_id'):
            emp_id = self.env['hr.employee'].sudo().browse(context.get('employee_id'))
            if emp_id.available_balance >= self.amount_total:
                self.env['employee.expenses'].sudo().create({
                    'name': emp_id.id,
                    'source': self.name,
                    'amount': self.amount_total
                })
            else:
                raise ValidationError(_('Sorry, You have not sufficient amount.'))
        if amount != 0.0:
            order_obj.add_payment(self.env.cr, self.env.uid, self.id, data, context=context)
            # Generate report attachment for email
            pdf_report = self.pool.get('report').get_pdf(self.env.cr, self.env.uid, [self.id],
                                'point_of_sale.report_receipt', data=None)
            attachment_data = {
                'name': "Receipt %s" % self.pos_reference,
                'datas_fname': 'Receipt.pdf',  # your object File Name
                'type': 'binary',
                'res_model': 'pos.order',
                'db_datas': pdf_report
            }
            attachment_id = self.pool.get('ir.attachment').create(self.env.cr, self.env.uid, attachment_data)
            if context.get('employee_id'):
                balance = self.employee_id.available_balance
                if self.employee_id.work_email:
                    self.sudo().send_email(self.id, self.employee_id.name, self.employee_id.work_email, attachment_id, balance)
            elif context.get('student_id'):
                balance = self.student_id.stud_balance_amount
                if self.student_id.partner_id.email:
                    self.send_email(self.id, self.student_id.partner_id.name, self.student_id.partner_id.email, attachment_id, balance)
        if order_obj.test_paid(self.env.cr, self.env.uid, [self.id]):
            order_obj.signal_workflow(self.env.cr, self.env.uid, [self.id], 'paid')
            return {'type' : 'ir.actions.act_window_close' }
        return self.env['pos.make.payment'].launch_payment()

    @api.one
    def multi_picking(self):
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        address = self.partner_id.address_get(['delivery']) or {}
        picking_type = self.picking_type_id
        order_picking = Picking
        return_picking = Picking
        return_pick_type = self.picking_type_id.return_picking_type_id or self.picking_type_id
        message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (self.id, self.name)
        if not self.partner_id.property_stock_customer:
            raise osv.except_osv(_('Error!'), _('Please configure Customer stock Location'))


        if self.partner_id:
            destination_id = self.partner_id.property_stock_customer.id
        else:
            if (not picking_type) or (
                    not picking_type.default_location_dest_id):
                customerloc, supplierloc = StockWarehouse._get_partner_locations()
                destination_id = customerloc.id
            else:
                destination_id = picking_type.default_location_dest_id.id
        copy_picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('default_location_dest_id', '=', destination_id)])
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('default_location_dest_id', '=', destination_id)], limit=1)
        location_ids = list(set([line.location_id.id for line in self.lines]))
        for loc_id in location_ids:
            picking_vals = {
                'origin': self.name,
                'partner_id': address.get('delivery', False),
                'date_done': self.date_order,
                'picking_type_id': self.session_id.config_id.picking_type_id.id,
                'company_id': self.company_id.id,
                'move_type': 'direct',
                'note': self.note or "",
                'location_id': loc_id,
                'location_dest_id': destination_id,
            }
            pos_qty = any(
                [x.qty > 0 for x in self.lines if x.product_id.type in ['product', 'consu']])
            if pos_qty:
                order_picking = Picking.create(picking_vals.copy())
                order_picking.message_post(body=message)
            neg_qty = any(
                [x.qty < 0 for x in self.lines if x.product_id.type in ['product', 'consu']])
            if neg_qty:
                return_vals = picking_vals.copy()
                return_vals.update({
                    'location_id': destination_id,
                    'location_dest_id': loc_id,
                    'picking_type_id': return_pick_type.id
                })
                return_picking = Picking.create(return_vals)
                return_picking.message_post(body=message)
            move_list = []
            for line in self.lines.filtered(
                lambda l: l.product_id.type in [
                    'product',
                    'consu'] and l.location_id.id == loc_id and not float_is_zero(
                    l.qty,
                    precision_digits=l.product_id.uom_id.rounding)):
                move_id = Move.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': loc_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else loc_id,
                })
                move_list.append(move_id.id)
            if return_picking:
                self.write({'picking_ids': [(4, return_picking.id)]})
                return_picking.action_confirm()
                return_picking.force_assign()
                return_picking.action_done()
            if order_picking:
                self.write({'picking_ids': [(4, order_picking.id)]})
                order_picking.sudo().action_confirm()
                order_picking.sudo().force_assign()
                order_picking.sudo().action_done()
            elif move_list:
                Move.action_confirm(move_list)
                Move.force_assign(move_list)
                Move.action_done(move_list)
        return True

    def create_picking(self, cr, uid, ids, context):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')
        
        for order in self.browse(cr, uid, ids):
            # custom multi location
            multi_loc = False
            for line_order in order.lines:
                if line_order.location_id:
                    multi_loc = True
                    break
            if multi_loc:
                order.multi_picking()
            else:
                if not order.lines.filtered(
                    lambda l: l.product_id.type in [
                        'product', 'consu']):
                    continue

                # Original Method
                addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
                picking_type = order.picking_type_id
                picking_id = False
                if picking_type:
                    picking_id = picking_obj.create(cr, uid, {
                        'origin': order.name,
                        'partner_id': addr.get('delivery', False),
                        'date_done' : order.date_order,
                        'picking_type_id': picking_type.id,
                        'company_id': order.company_id.id,
                        'move_type': 'direct',
                        'note': order.note or "",
                        'invoice_state': 'none',
                    }, context=context)
                    self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
                location_id = order.stock_location_id.id

                if not order.partner_id.property_stock_customer:
                    raise osv.except_osv(_('Error!'), _('Please configure Customer stock Location'))

                if order.partner_id:
                    destination_id = order.partner_id.property_stock_customer.id
                elif picking_type:
                    if not picking_type.default_location_dest_id:
                        raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                    destination_id = picking_type.default_location_dest_id.id
                else:
                    destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']
    
                move_list = []
                for line in order.lines:
                    if line.product_id and line.product_id.type == 'service':
                        continue
    
                    move_list.append(move_obj.create(cr, uid, {
                        'name': line.name,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uos': line.product_id.uom_id.id,
                        'picking_id': picking_id,
                        'picking_type_id': picking_type.id,
                        'product_id': line.product_id.id,
                        'product_uos_qty': abs(line.qty),
                        'product_uom_qty': abs(line.qty),
                        'state': 'draft',
                        'location_id': location_id if line.qty >= 0 else destination_id,
                        'location_dest_id': destination_id if line.qty >= 0 else location_id,
                    }, context=context))
            
                if picking_id:
                    order.write({'picking_ids': [(4, picking_id)]})
                    picking_obj.action_confirm(cr, SUPERUSER_ID, [picking_id], context=context)
                    picking_obj.force_assign(cr, SUPERUSER_ID, [picking_id], context=context)
                    picking_obj.action_done(cr, SUPERUSER_ID, [picking_id], context=context)
                elif move_list:
                    move_obj.action_confirm(cr, SUPERUSER_ID, move_list, context=context)
                    move_obj.force_assign(cr, SUPERUSER_ID, move_list, context=context)
                    move_obj.action_done(cr, SUPERUSER_ID, move_list, context=context)
        return True

    def generate_order_pos_reference(self, cr, uid, ids, number, size, context=None):
        pos_reference = "" + str(number)
        while len(pos_reference) < size:
            pos_reference = "0" + pos_reference
        return pos_reference

    def create(self, cr, uid, values, context=None):
        res = super(pos_order, self).create(cr, uid, values, context)
        order_id = self.browse(cr, uid, res)
        if values.get('employee_id') or values.get('student_id'):
            if values.get('employee_id'):
                if order_id and order_id.amount_total > order_id.employee_id.available_balance:
                    raise ValidationError(_('Sorry, You have not sufficient amount.'))
            if values.get('student_id'):
                if order_id and order_id.amount_total > order_id.student_id.stud_balance_amount:
                    raise ValidationError(_('Sorry, You have not sufficient amount.'))
            order_id.write({'is_self_service':True})
            if not values.get('pos_reference'):
                session_id = self.pool.get('pos.session').browse(cr, uid, [values.get('session_id')])
                if session_id:
                    values['pos_reference'] = self.generate_order_pos_reference(cr, uid, [], session_id.id, 5) + '-' + \
                       self.generate_order_pos_reference(cr, uid, [] , session_id.login_number, 3) + '-' + \
                       self.generate_order_pos_reference(cr, uid, [], session_id.sequence_number, 4);
                    order_id.write({'pos_reference':_("Order ") + values['pos_reference']})
                    session_id.write({'sequence_number' : session_id.sequence_number + 1})
        return res

    def _order_fields(self, cr, uid, ui_order, context=None):
        ofields = super(pos_order, self)._order_fields(cr, uid, ui_order, context)
        ofields.update({
            'student_id': ui_order.get('student_id'),
            'employee_id': ui_order.get('faculty_id'),
            'is_self_service':ui_order.get('is_self_service'),
            'is_from_pos':ui_order.get('is_from_pos'),
        })
        return ofields

    def _process_order(self, cr, uid, order, context=None):
        session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)

        ## Get Partnet Id For  selected Employee
        emp_obj = self.pool.get('hr.employee')
        if order.get('faculty_id'):
            emp_data = emp_obj.search(cr, uid, [('id', '=', order.get('faculty_id'))])
            emp_id = emp_obj.browse(cr, uid, emp_data)
            ## Update partner Id for selected user here its employee/faculty
            if emp_id and emp_id.user_id:
                order['partner_id'] = emp_id.user_id.partner_id.id

        ## Get Partnet Id For S selected student
        # student_obj = self.pool.get('op.student')
        # if order.get('student_id'):
        #     student_data = student_obj.search(cr, uid, [('id', '=', order.get('student_id'))])
        #     student_id = student_obj.browse(cr, uid, student_data)
        #     ## Update partner Id for selected user here its student
        #     if student_id:
        #         order['partner_id'] = student_id.partner_id.id


        if session.state == 'closing_control' or session.state == 'closed':
            session_id = self._get_valid_session(cr, uid, order, context=context)
            session = self.pool.get('pos.session').browse(cr, uid, session_id, context=context)
            order['pos_session_id'] = session_id

        order_id = self.create(cr, uid, self._order_fields(cr, uid, order, context=context),context)
        journal_ids = set()
        for payments in order['statement_ids']:
            self.add_payment(cr, uid, order_id, self._payment_fields(cr, uid, payments[2], context=context), context=context)
            journal_ids.add(payments[2]['journal_id'])

        if session.sequence_number <= order['sequence_number']:
            session.write({'sequence_number': order['sequence_number'] + 1})
            session.refresh()

        if not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')):
            cash_journal = session.cash_journal_id.id
            if not cash_journal:
                # Select for change one of the cash journals used in this payment
                cash_journal_ids = self.pool['account.journal'].search(cr, uid, [
                    ('type', '=', 'cash'),
                    ('id', 'in', list(journal_ids)),
                ], limit=1, context=context)
                if not cash_journal_ids:
                    # If none, select for change one of the cash journals of the POS
                    # This is used for example when a customer pays by credit card
                    # an amount higher than total amount of the order and gets cash back
                    cash_journal_ids = [statement.journal_id.id for statement in session.statement_ids
                                        if statement.journal_id.type == 'cash']
                    if not cash_journal_ids:
                        raise osv.except_osv( _('error!'),
                            _("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0]
            self.add_payment(cr, uid, order_id, {
                'amount': -order['amount_return'],
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal,
            }, context=context)
        return order_id

    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
        existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]

        order_ids = []

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            order_id = self._process_order(cr, uid, order, context=context)
            order_ids.append(order_id)
            try:
                self.signal_workflow(cr, uid, [order_id], 'paid')
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            product_obj = self.pool.get('product.product')
            for line in order.get('lines'):
                if line[2].get('product_id'):
                    product = product_obj.browse(cr, uid, line[2].get('product_id'))
                    if product and product.id:
                        product.write({'dummy_qty_update':True})
            if to_invoice:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')
            # create student expense
            if order.get('student_id'):
                self.pool['student.expenses'].create(cr, uid, {
                    'name': order.get('student_id'),
                    'source': order.get('name'),
                    'amount': order.get('amount_total')
                })
            # create employee expense
            if order.get('faculty_id'):
                self.pool['employee.expenses'].create(cr, uid, {
                    'name': order.get('faculty_id'),
                    'source': order.get('name'),
                    'amount': order.get('amount_total')
                })
            # Generate report attachment for email
            pdf_report = self.pool.get('report').get_pdf(cr, uid, [order_id],
                                'point_of_sale.report_receipt', data=None)
            attachment_data = {
                'name': "Receipt %s" % order.get('name'),
                'datas_fname': 'Receipt.pdf',  # your object File Name
                'type': 'binary',
                'res_model': 'pos.order',
                'db_datas': pdf_report
            }
            attachment_id = self.pool.get('ir.attachment').create(cr, uid, attachment_data)
            # send SMS and Email for Employee
            if order.get('faculty_id'):
                employee = self.pool['hr.employee'].browse(cr, uid, order['faculty_id'])
                if employee.mobile_phone:
                    message = """Hi %s, Your account has been debited %s. Your current balance is %s. Regards""" % (employee.name, order['amount_total'], employee.available_balance)
                    self.pool['sms.config'].send_sms(cr, uid, employee.mobile_phone, message)
                if employee.work_email:
                    self.send_email(cr, uid, order_id, employee.name, employee.work_email,
                                    attachment_id, employee.available_balance)
        return order_ids

    def send_email(self, cr, uid, order_id, receiver, email, attachment_id, balance_amount):
        """
        Send email to everyone for every sales from POS
        :param order_id:
        :return:
        """
        mail_obj = self.pool['mail.mail']
        order = self.browse(cr, uid, order_id)
        mail_message = """<p>Dear %s,</p>
<p>Welcome to the Self Service Point of Sale. You have just been debited of the amount %s. Your available balance is now %s</p>
<p>Your ticket number is %s .</p>
<p>Thanks for using this Service.</p>

<p>Regards,</p>
<p> E-Wallet Admin</p>
""" % (receiver, order.amount_total, balance_amount, order.pos_reference)
        values = {
            'subject': 'Regarding Sales Status',
            'body_html': mail_message,
            'email_to': email,
            'email_from': 'noreply@localhost',
        }
        if attachment_id:
            values.update({'attachment_ids': [(6, 0, [attachment_id])]})
        msg_id = mail_obj.create(cr, uid, values)
        try:
            mail_obj.send(cr, uid, [msg_id])
        except:
            _logger.error(_('Unable to send email for order %s' % order.name))
        return True


class stock_location(models.Model):
    _inherit = "stock.location"

    category_ids = fields.Many2many('pos.category', 'stock_loca_prod_categ', 'prod_categ_id', 'loc_id', 'POS Categories')


class product_product(models.Model):
    _inherit = "product.product"

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name','')
            code = context.get('display_default_code', True) and d.get('default_code',False) or False
            if code:
                name = '%s' % (name)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context and self._context.get('from_wiz_order_id'):
            if not args:
                args = []
            location_id = self.env['stock.location'].browse(self._context['from_wiz_order_id'])
            if location_id:
                pos_categ_lst = [categ.id for categ in location_id.category_ids]
                args += [('pos_categ_id', 'in', pos_categ_lst)]
                return super(product_product, self).name_search(name, args=args, operator=operator, limit=limit)
        else:
            return super(product_product, self).name_search(name, args=args, operator=operator, limit=limit)

class product_template(models.Model):
    _inherit = "product.template"

    dummy_qty_update = fields.Boolean("Quantity Update")

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    location_id = fields.Many2one('stock.location', string='Location')
    copy_price_unit = fields.Float('Unit Price', readonly=True, compute="update_unit_amt", store=True)
    image = fields.Binary(related='product_id.image_medium', string='Image', readonly=True)

    ## Show procut avail qty and current available qty
    pro_current_available_qty = fields.Integer('Available Qty')

    ## Add fields for expanded reports
    partner_id = fields.Many2one(related="order_id.partner_id", string='Customer')
    order_state = fields.Selection(related="order_id.state", string='State')
    pos_referance = fields.Char(related="order_id.pos_reference", string='Receipt Ref')
    date_order = fields.Datetime(related="order_id.date_order", string='Date')

    def create(self, cr, uid, values, context=None):
        res = super(PosOrderLine, self).create(cr, uid, values, context)
        pol_id = self.browse(cr, uid, res)
        match_line_ids = self.search(cr, uid, [('product_id', '=', values.get('product_id')), ('order_id', '=', values.get('order_id'))])
        used_qty = 0
        for line in self.browse(cr, uid, match_line_ids):
            used_qty = used_qty + line.qty
        prod_id = self.pool['product.product'].browse(cr, uid, values.get('product_id'))
        if not pol_id.order_id.is_from_pos:
            if pol_id.order_id and pol_id.order_id.is_self_service and prod_id.qty_available < values.get('qty') + used_qty and prod_id.type != 'service':
                raise ValidationError(_('You are exceeding the stock limit of %s for "%s"') % (prod_id.qty_available, prod_id.name))
        return res

    @api.depends('product_id')
    def update_unit_amt(self):
        for rec in self:
            rec.copy_price_unit = rec.price_unit

    @api.constrains('product_id', 'qty')
    def check_qty(self):
        if not self.order_id and self.order_id.is_from_pos:
            if self.order_id and self.order_id.is_self_service and self.qty > self.product_id.qty_available and self.product_id.type != 'service':
                raise ValidationError(_('Only %s quantity left for "%s"') % (self.product_id.qty_available, self.product_id.name))


class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def disp_prod_stock(self, product_id, shop_id):
        stock_line = []
        total_qty = 0
        shop_qty = 0
        quant_obj = self.env['stock.quant']
        for warehouse_id in self.search([]):
            product_qty = 0.0
            ware_record = warehouse_id
            location_id = ware_record.lot_stock_id.id
            if shop_id:
                loc_ids1 = self.env['stock.location'].search(
                    [('location_id', 'child_of', [shop_id])])
                stock_quant_ids1 = quant_obj.search([('location_id', 'in', [
                                                    loc_id.id for loc_id in loc_ids1]), ('product_id', '=', product_id)])
                for stock_quant_id1 in stock_quant_ids1:
                    shop_qty = stock_quant_id1.qty

            loc_ids = self.env['stock.location'].search(
                [('location_id', 'child_of', [location_id])])
            stock_quant_ids = quant_obj.search([('location_id', 'in', [
                                               loc_id.id for loc_id in loc_ids]), ('product_id', '=', product_id)])
            for stock_quant_id in stock_quant_ids:
                product_qty += stock_quant_id.qty
            stock_line.append([ware_record.name, product_qty,
                               ware_record.lot_stock_id.id])
            total_qty += product_qty
        return stock_line, total_qty, shop_qty
