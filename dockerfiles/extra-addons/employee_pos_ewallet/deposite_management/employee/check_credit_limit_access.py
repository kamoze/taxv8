from openerp import models, fields, api
from openerp.osv import osv
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    """ Set access rights for credit limit """

    @api.model
    def is_sales_rep(self):
        ''' Function to check user if it is  Default sales rep in case of Sales Rep Logged in'''
        group_id = self.env['ir.model.data'].get_object_reference(
            'account', 'group_account_manager')
        group_id = group_id and group_id[1] or False
        group_rec = self.env['res.groups'].browse(group_id)
        group_user_ids = [x.id for x in group_rec.users]
        if self._uid in group_user_ids:
            return True
        else:
            return False

    @api.model
    def fields_view_get(self, view_id=None,
                        view_type='form', context=None,
                        toolbar=False, submenu=False):
        context = context or {}
        res = super(HrEmployee, self). \
            fields_view_get(
            view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu)

        if view_type == "form":
            if not self.is_sales_rep():
                doc = etree.XML(res['arch'])
                # for node in doc.xpath("//field[@name='user_id']"):
                #     node.set('options', '{"no_open": True, "no_create": True}')
                for node in doc.xpath("//field[@name='credit_limit']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, res['fields']['credit_limit'])
                res['arch'] = etree.tostring(doc)
        return res
