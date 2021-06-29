from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, datetime, timedelta
import time
from openerp.exceptions import except_orm
import random
from openerp import SUPERUSER_ID

""" Model for creating tax payer profile """


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'



    def compute_tin(self, cr, uid, ids, context=None):

        v = {}
        for tax_id in self.browse(cr, uid, ids, context=context):

            if (tax_id.is_company is True) and (tax_id.e_tax is True):
                code = 'co'
                a = 'id'
                today = date.today()
                year = str(today.year)
                identity = str(tax_id.id)
                final_tin = code + year + a + identity
                v['vat'] = final_tin

            if (tax_id.is_employed is True) and (tax_id.e_tax is True):
                code = 'emp'
                a = 'id'
                today = date.today()
                year = str(today.year)
                identity = str(tax_id.id)
                final_tin = code + year + a + identity
                v['vat'] = final_tin

            if (tax_id.is_self_employed is True) and (tax_id.e_tax is True):
                code = 'semp'
                a = 'id'
                today = date.today()
                year = str(today.year)
                identity = str(tax_id.id)
                final_tin = code + year + a + identity
                v['vat'] = final_tin

        self.write(cr, uid, ids, v)
        return True

    def send_tin(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        email_template_obj = self.pool.get('email.template')
        template_ids = email_template_obj.search(cr, uid, [('name', '=', 'Send TIN as Mail to Tax Payer')],
                                                 context=context)
        #         try:
        #             template_id = ir_model_data.get_object_reference(cr, uid, 'isa_crm_helpdesk', 'email_template_edi_purchase')[1]
        #         except ValueError:
        #             template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[
                1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'res.partner',
            'default_res_id': ids[0],
            'default_use_template': bool(template_ids),
            'default_template_id': template_ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    _columns = {
        'number': fields.char('No.'),
        'is_corporate': fields.boolean('Is a Corporate'),
        'is_employed': fields.boolean('Is Employed'),
        'is_self_employed': fields.boolean('Is Self Employed'),
        'e_tax': fields.boolean('e-Tax'),
        'last_name': fields.char('Surname', required=True),
        'other_name': fields.char('Other name'),
        'date_of_birth': fields.date('Date of Birth'),
        'sex': fields.selection([('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], 'Sex'),
        'marital_state': fields.selection(
            [('single', 'Single'), ('married', 'Married'), ('divorce', 'Divorce'), ('widow', 'Widow')],
            'Marital Status'),
        'nationality': fields.many2one('res.country', 'Nationality'),
        'postal_street': fields.char('Street'),
        'postal_street2': fields.char('Street2'),
        'local_govt_city': fields.char('Local Govt Area'),
        'trade_name': fields.char('Trade Name'),
        'self_employed_business': fields.integer('No. of Self-employed Businesses'),
        'business_names': fields.integer('Total No. of Businesses'),
        'property_income_receive': fields.selection([('y', 'Yes'), ('n', 'No')],
                                                    'Did you receive income from Nigerian properties including land in the current tax year?'),
        'dispose_of_chargeable_assets': fields.selection([('y', 'Yes'), ('n', 'No')],
                                                         'Did you dispose of any chargeable assets within the current tax year?'),
        'interest_income_receive': fields.selection([('y', 'Yes'), ('n', 'No')],
                                                    'Did you receive any Interests from any Nigerian banks, building Societies, and Trusts?'),
        'dividend_income_receive': fields.selection([('y', 'Yes'), ('n', 'No')],
                                                    'Did you receive any Dividends within the current tax Year?'),
        'pasb_income_receive': fields.selection([('y', 'Yes'), ('n', 'No')],
                                                'Did you receive any Nigerian Pensions, Annuities, or State Benefits, for example, State Pension, Occupational Pension, Retirement Annuity, Disability Benefits ?'),
        'over_income_receive': fields.selection([('y', 'Yes'), ('n', 'No')], 'Was you income over N300,000 ?'),
        'origin_state_id': fields.many2one('res.country.state', 'Origin State'),
        'postal_zip': fields.char('ZIP'),
        'postal_country_id': fields.many2one('res.country', 'Country'),
        'business_type': fields.char('Type/Nature of Business'),
        'business_name': fields.char('Name of the Business'),
        'office_street': fields.char('Street'),
        'office_street2': fields.char('Street2'),
        'office_city': fields.char('City'),
        'office_state_id': fields.many2one('res.country.state', 'State'),
        'office_zip': fields.char('ZIP'),
        'office_country_id': fields.many2one('res.country', 'Country'),
        'office_phone': fields.char('Phone'),
        'office_mobile': fields.char('Mobile'),
        'passport_number': fields.char('Passport'),
        'passport_validity_date': fields.date('Date'),
        'tax_office': fields.many2one('etax.tax.office', 'Nearest Tax Office'),
        'approve_state': fields.selection([('new', 'New'),
                                           ('review', 'Reviewed'),
                                           ('approve', 'Approved'),
                                           ('request', 'Tin Requested'),
                                           ('generate', 'Tin Genereated'),
                                           ('rejected', 'Rejected'),
                                           ('not_approved', 'Not Approved'),

                                           ], 'State', track_visibility='onchange'),
        'tax_config_id': fields.many2one('tax.configuration', 'Tax Configuration Id'),
        'generate_tin': fields.boolean('Generate TIN'),
        'tin': fields.char('FIRS TIN'),
        'select_tin': fields.selection([('tinn', 'Tin'), ('tin_menu', 'Tin Menu'), ('tin_vals', 'Tin Vals')],
                                       'Select Tin'),
        'distrain_process': fields.selection([('no_distrain', 'No Distrain'),
                                              ('new_distrain', 'New'),
                                              ('issue_notice', 'Issue Notice'),
                                              ('payment_done', 'Payment Done'),
                                              ('close', 'Distrain Close'),
                                              ('count_order', 'Count Order'),
                                              ('warrent', 'Warrent')],
                                             'Distrain Process', readonly=True),
        'country': fields.char('Country'),
        'type_tax': fields.selection(
            [('corporate', 'Corporate'), ('employed', 'Emp;oyed'), ('self_employed', 'Self Employed')], 'Type Tax'),
        'reject': fields.text(' Reason for Rejection'),
        'number': fields.many2one('partner.application.form','Application Reference'),
        'tax_office_id': fields.many2one('etax.tax.office', ' Tax Office'),
        'bvn': fields.char('BVN'),

        'license_no': fields.char('Drivers License No.'),
        'national_id': fields.char('National ID No.'),
        'reject': fields.text('Reason for Rejection'),


    }
    _defaults = {
        'select_tin': 'tinn',
        'approve_state': 'new',
        'distrain_process': 'no_distrain'
    }

    def write(self, cr, uid, ids, vals, context=None):
        #         if self.browse(cr,uid,ids[0]).select_tin=='tin_menu':
        for data in self.browse(cr, uid, ids):
            print ":())(:::::::", data.name
            if data.select_tin == 'tin_menu':
                if 'tin' in vals:
                    vals['select_tin'] = 'tin_vals'
                    mail_mail = self.pool.get('mail.mail')
                    #                     mail_id = mail_mail.create(cr, uid, {
                    #                                     'model': 'tax.calculator.individual',
                    # #                                     'res_id': ids[0],
                    #                                     'subject': 'Tax Profile is Approved',# 'Invitation to follow %s' % document.name_get()[0][1],
                    #                                     'body_html':'Dear Sir,' + '\n' + 'Your TIN is Generated',
                    #                                     'auto_delete': False,
                    #                                     }, context=context)
                    #                     print 'MAILJID::::::'
                    #                     mail_mail.send(cr, uid, [mail_id], recipient_ids=[self.browse(cr,uid,ids[0]).name.id], context=context)
        result = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        return result

    # def app_form_to_profile(self,cr,uid,ids,context=None):



    def name_get(self, cr, uid, ids, context=None):

        vals = super(res_partner, self).name_get(cr, uid, ids, context)
        vals_list = []
        for rec in vals:
            br_rec = self.browse(cr, uid, rec[0], context)
            name = []
            if br_rec.last_name and br_rec.other_name:
                name = br_rec.name + ' ' + str(br_rec.last_name) + ' ' + str(br_rec.other_name)
            elif br_rec.last_name:
                name = br_rec.name + ' ' + str(br_rec.last_name)
            elif br_rec.other_name:
                name = br_rec.name + ' ' + str(br_rec.other_name)
            else:
                name = br_rec.name
            vals_list.append((rec[0], name))

        return vals_list

    def onchange_is_employed(self, cr, uid, ids, is_employed, context=None):
        v = {}
        if is_employed is True:
            v['is_company'] = False
            v['is_self_employed'] = False
        return {'value': v}

    def onchange_is_self_employed(self, cr, uid, ids, is_self_employed, context=None):
        v = {}
        if is_self_employed is True:
            v['is_company'] = False
            v['is_self_employed'] = False
        return {'value': v}

    def onchange_company(self, cr, uid, ids, parent_id, context=None):
        v = {}
        if parent_id:
            company_obj = self.pool.get('res.partner').browse(cr, uid, parent_id)
            v['office_street'] = company_obj.street
            v['office_street2'] = company_obj.street2
            v['office_city'] = company_obj.city
            v['office_state_id'] = company_obj.state_id.id
            v['office_zip'] = company_obj.zip
            v['office_country_id'] = company_obj.country_id.id

        return {'value': v}

    def generate(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cr.execute("select tin_prefix from tax_configuration")
        config_res = cr.fetchone()
        if not config_res:
            raise except_orm(_('No Configuration Found!'),
                             _("Please configure TIN Prefix Under Tax Configuration' !"))
        prefix = config_res and config_res[0] or ''
        randon_value = random.randint(0000001, 9999999)
        number = str(prefix) + str(randon_value)
        old_ids = self.search(cr, SUPERUSER_ID, [('tin','=',number)])
        if old_ids:
            self.generate(cr, uid, ids)

        is_employed = is_self_employed = corporte = False
        if obj.application_type == 'self_employed':
            is_self_employed = True
        elif obj.application_type == 'employed':
            is_employed = True
        elif obj.application_type == 'corporte':
            corporte = True
        self.write(cr, uid, [ids[0]], {'generate_tin': True, 'select_tin': 'tin_menu','e_tax': True,'is_self_employed':is_self_employed,
                                       'tin': number, 'approve_state': 'generate','is_employed':is_employed, 'is_corporate': corporte})
        return True

    def action_approve(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        list = []
        group_ids = []
        list_group = []
        for vals in self.browse(cr, uid, ids):
            if vals.user_id:
                for val in vals.user_id.groups_id:
                    list.append(val.id)
                obj_group_ids = self.pool.get('res.groups')
                grp_ids = obj_group_ids.search(cr, uid, [('name', '=', 'Tax Assesment')], context=context)
                grp_ids1 = obj_group_ids.search(cr, uid, [('name', '=', 'Tax Office')], context=context)
                grp_ids2 = obj_group_ids.search(cr, uid, [('name', '=', 'Tax Forms')], context=context)
                grp_ids4 = obj_group_ids.search(cr, uid, [('name', '=', 'E-Tax User')], context=context)

                list_group = list + grp_ids + grp_ids2 + grp_ids4
            if vals.type_tax == 'self_employed':
                group_ids = obj_group_ids.search(cr, uid, [('name', '=', 'Self Employed')], context=context)
            elif vals.type_tax == 'employed':
                group_ids = obj_group_ids.search(cr, uid, [('name', '=', 'Employed')], context=context)
            elif vals.type_tax == 'corporate':
                group_ids = obj_group_ids.search(cr, uid, [('name', '=', 'Corporate')], context=context)
            list_group_ids = list_group + group_ids
            self.pool.get('res.users').write(cr, uid, [vals.user_id.id], {'groups_id': [(6, 0, list_group_ids)]})

        mail_mail = self.pool.get('mail.mail')
        # mail_id = mail_mail.create(cr, uid, {
        #                 'model': 'tax.calculator.individual',
        #                 'res_id': ids[0],
        #                 'subject': 'Tax Profile is Approved',# 'Invitation to follow %s' % document.name_get()[0][1],
        #                 'body_html':'Dear Sir,' + '\n' + 'Your Tax Profile is Approved',
        #                 'auto_delete': False,
        #                 }, context=context)
        # print "mai_id================",mail_id
        # mail_mail.send(cr, uid, [mail_id], recipient_ids=[self.browse(cr,uid,ids[0]).name.id], context=context)

        self.write(cr, uid, [ids[0]], {'approve_state': 'approve'})
        return True
    def request_tin(self, cr, uid, ids, context=None):

        return self.write(cr, uid, ids, {'approve_state': 'request', 'select_tin': 'tin_menu'}, context=context)

    def action_request_to_approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'approve_state': 'not_approved'}, context=context)

    def action_rejected(self, cr, uid, ids, context=None):
        data = self.browse(cr,uid, ids, context=context)
        appication = self.pool.get('partner.application.form').search(cr, uid, [('res_ptnr_id', '=', data.id)])

        if not data.reject:
            raise except_orm(_('No Configuration Found!'),
                             _("Please Provide the reason for Rejection' !"))
        self.write(cr, uid, ids, {'approve_state': 'rejected'}, context=context)
        if appication:
            self.pool.get('partner.application.form').write(cr, uid,appication, {'approve_state': 'rejected', 'is_approve': False}, )

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }, ''


    # def unlink(self, cr, uid, ids, context=None):
    #     unlink_ids = []
    #     unlink_product_tmpl_ids = []
    #
    #     partner_ids = self.search(cr, uid, [('approve_state', '=', 'rejected')])
    #     for partner in partner_ids:
    #         unlink_ids.append(partner)
    #     res = super(res_partner, self).unlink(cr, uid, unlink_ids, context=context)
    #
    #     return res



class etax_tax_office(osv.osv):
    _name = 'etax.tax.office'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char('Name of the tax office', required=True),
        'city': fields.char('City', required=True),
        'state_id': fields.many2one('res.country.state', 'State', required=True),
        'tax_config_id': fields.many2one('tax.configuration', 'Tax Configuration'),
    }

class etax_attachment(osv.osv):
    _name = 'etax.attachment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    _columns = {
        'name': fields.char('Name', required=True),

        'attachments_id': fields.binary('Attachment', required=True),
        'datas': fields.char('data')

    }


class tax_configuration(osv.osv):
    _name = 'tax.configuration'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns={
              'name':fields.char('TIN Prefix',required=False),
              'tin_prefix': fields.char('TIN Prefix', size=3),
              'product':fields.many2one('product.product','Product'),
              'assessment_charges_product':fields.many2one('product.product','Assesment Charges Product'),
              'admin_charges_product':fields.many2one('product.product','Admin Charges Product'),
              'assessment_charges':fields.float('Assessment Charges'),
              'admin_charges':fields.float('Admin Charges'),
              'companies_income_tax':fields.float('Companies Income Tax'),
              'petroleurm_profit_tax':fields.float('Petroleum Profit Tax'),
              'education_tax':fields.float('Education Tax'),
              'technology_levy':fields.float('Technology Levy'),
              'companies_income_product':fields.many2one('product.product','Companies Income Tax Product'),
              'petroleurm_profit_product':fields.many2one('product.product','Petoleum Profit Tax Product'),
              'education_tax_product':fields.many2one('product.product','Education Tax Product'),
              'technology_levy_product':fields.many2one('product.product','Technology Levy Product'),
              'account_tax_id':fields.many2many('account.tax','tax_configuration_account_rel','tax_configuration_id','account_tax_id',string="Other Taxes"),


              }


    _defaults = {
        'name': 'Tax Configuration'
    }


class etax_claim(osv.osv):
    _name = 'etax.claim'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'E-tax Claim'

    _columns = {
        'name': fields.char('Name'),
        'state': fields.selection(
            [('draft', 'New'), ('submit', 'Submit'), ('accept', 'Accept'), ('reject', 'Reject'), ('done', 'Done')],
            'State', track_visibility='onchange'),
        'submit_date': fields.datetime('Submit Date'),
        'accept_date': fields.datetime('Accept Date'),
        'reject_date': fields.datetime('Reject Date'),
        'done_date': fields.datetime('Done Date'),
        'partner_id': fields.many2one('res.partner', 'Profile'),
        'user_id': fields.many2one('res.users', 'User'),
        'tax_id': fields.many2one('tax.calculator.individual', 'Assessment Id'),
        'comment': fields.text('Description '),

    }

    def _get_default_partner_id(self, cr, uid, context=None):
        partner_id = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
        return partner_id

    _defaults = {
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_id': _get_default_partner_id,
        'tax_id': lambda obj, cr, uid, context: uid,

    }

    def action_submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'submit', 'submit_date': time.strftime('%Y-%m-%d')}, context=context)

    def action_accept(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'accept', 'accept_date': time.strftime('%Y-%m-%d')}, context=context)

    def action_reject(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'reject', 'reject_date': time.strftime('%Y-%m-%d')}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done', 'done_date': time.strftime('%Y-%m-%d')}, context=context)

