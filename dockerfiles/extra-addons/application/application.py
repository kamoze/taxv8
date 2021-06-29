from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, ustr
from datetime import date
import openerp
from openerp.http import request
import time
from ast import literal_eval
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import random


class SignupError(Exception):
    pass


class AuthSignupHome(openerp.addons.web.controllers.main.Home):
    inherit = 'AuthSignupHome'

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password', 'login_type'))
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()


class res_users(osv.Model):
    _inherit = 'res.users'

    #     def _get_group(self,cr, uid, context=None):
    #         dataobj = self.pool.get('ir.model.data')
    #         result = []
    #         try:
    # #             dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_user')
    # #             result.append(group_id)
    #             dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_partner_manager')
    #             result.append(group_id)
    #         except ValueError:
    #             # If these groups does not exists anymore
    #             pass
    #         return result

    #     def write(self, cr, uid, ids, vals, context=None):
    #         result = super(res_users, self).write(cr, uid, ids, vals, context=context)
    #         return result

    def _signup_create_user(self, cr, uid, values, context=None):
        """ create a new user from the template user """
        ir_config_parameter = self.pool.get('ir.config_parameter')
        template_user_id = literal_eval(ir_config_parameter.get_param(cr, uid, 'auth_signup.template_user_id', 'False'))
        assert template_user_id and self.exists(cr, uid, template_user_id,
                                                context=context), 'Signup: invalid template user'

        # check that uninvited users may sign up
        if 'partner_id' not in values:
            if not literal_eval(ir_config_parameter.get_param(cr, uid, 'auth_signup.allow_uninvited', 'False')):
                raise SignupError('Signup is not allowed for uninvited users')

        assert values.get('login'), "Signup: no login given for new user"
        assert values.get('partner_id') or values.get('name'), "Signup: no name or partner given for new user"

        # create a copy of the template user (attached to a specific partner_id if given)
        values['active'] = True
        context = dict(context or {}, no_reset_password=True)
        groups_obj = self.pool.get('res.groups')
        group_id = groups_obj.search(cr, uid, [('name', '=', 'Portal')])
        emp_grp_id = groups_obj.search(cr, uid, [('name', '=', 'Employee')])
        tx_gp_id = groups_obj.search(cr, uid, [('name', '=', 'E-Tax Payer')])
        corp_id = groups_obj.search(cr, uid, [('name', '=', 'Corporate')])
        indi_id = groups_obj.search(cr, uid, [('name', '=', 'Self Employed')])
        indi1_id = groups_obj.search(cr, uid, [('name', '=', 'Employed')])
        assesment_id = groups_obj.search(cr, uid, [('name', '=', 'Tax Assesment')])
        account_id = groups_obj.search(cr, uid, [('name', '=', 'Tax Accounting')])
        group_ids = tx_gp_id + assesment_id + account_id + group_id + emp_grp_id
        individiual = indi_id + indi1_id
        if values.get('login_type') == 'individual':
            group_ids += individiual
        elif values.get('login_type') == 'corporate':
            group_ids += corp_id

        try:
            with cr.savepoint():
                new_id = self.copy(cr, uid, template_user_id, values, context=context)
                # groups_obj.write(cr, uid, group_id, {'users': [(3, new_id)],})
                groups_obj.write(cr, uid, group_ids, {'users': [(4, new_id)], })
                # groups_obj.write(cr, uid, tx_gp_id, {'users': [(4, new_id)],})
                return new_id
        except Exception, e:
            # copy may failed if asked login is not available.
            raise SignupError(ustr(e))


class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'approve_state': fields.selection([('new', 'New'),
                                           ('review', 'Reviewed'),
                                           ('approve', 'Approved'),
                                           ('request', 'Tin Requested'),
                                           ('generate', 'Tin Genereated'),
                                           ('rejected', 'Rejected'),
                                           ('not_approved', 'Not Approved'),

                                           ], 'State', track_visibility='onchange'),
        'application_state': fields.selection([('new', 'New'), ('review', 'Review'), ('approve', 'Approved')], 'State'),
        'application_type': fields.selection(
            [('self_employed', 'Self Employed'), ('employed', 'Employed'), ('corporate', 'Corporate')], 'Type'),
        'is_approve': fields.boolean('Approve'),
        'rs_ur_id': fields.many2one('res.users', 'User'),


    }

    _defaults = {
        'rs_ur_id': lambda self, cr, uid, context: uid,

    }


class partner_application_form(osv.osv):
    _name = 'partner.application.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherits = {'res.partner': 'res_ptnr_id'}
    _rec_name = 'number'

    #     def use_own_address(self,cr,uid,ids,context=None):
    #         v={}
    #         if ids:
    #             address_obj = self.browse(cr,uid,ids,context=None)
    #             v['postal_street'] = address_obj.street
    #             v['postal_street2'] = address_obj.street2
    #             v['postal_city'] = address_obj.city
    #             v['postal_state_id'] = address_obj.state_id.id
    #             v['postal_zip'] = address_obj.zip
    #             v['postal_country_id'] = address_obj.country_id.id
    #
    #         return{'value':v}

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
        'res_ptnr_id': fields.many2one('res.partner', 'Partner', required=True, ondelete="cascade", select=True,
                                       auto_join=True),
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
        'business_names': fields.integer('Name of  Businesses'),
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
        'tax_office_id': fields.many2one('etax.tax.office', ' Tax Office'),
        'approve_state': fields.selection([('new', 'New'), ('review', 'Review'), ('approve', 'Approved'), ], 'State'),
        'tax_config_id': fields.many2one('tax.configuration', 'Tax Configuration Id'),
        'generate_tin': fields.boolean('Generate Tin'),
        'tin': fields.char('TIN'),
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
            [('corporate', 'Corporate'), ('employed', 'Employed'), ('self_employed', 'Self Employed')], 'Type Tax'),
        'approve_state': fields.selection(
            [('new', 'New'), ('review', 'Review'), ('not_approved', 'Not Approved'), ('approve', 'Approved'),
             ('rejected', 'Rejected')], 'State', ),
        'bvn': fields.char('BVN'),
        'driver_license': fields.char('Driver License No.'),
        'national_id': fields.char('National ID No.'),
        'reject': fields.text('Reason for Rejection'),


        #         'application_state':fields.selection([('new','New'),('review','Review'),('approve','Approved')],'State'),
        #         'application_type':fields.selection([('self_employed','Self Employed'),('employed','Employed'),('corporate','Corporate')],'Type'),
        #         'is_approve' : fields.boolean('Approve'),

    }
    _defaults = {
        'select_tin': 'tinn',
        'approve_state': 'new',
        'distrain_process': 'no_distrain',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def unlink(self, cr, uid, ids, context=None):
        unlink_ids = []
        unlink_product_tmpl_ids = []
        for product in self.browse(cr, uid, ids, context=context):
            # Check if product still exists, in case it has been unlinked by unlinking its template
            if not product.exists():
                continue
            tmpl_id = product.res_ptnr_id.id
            # Check if the product is last product of this template
            other_product_ids = self.search(cr, uid, [('res_ptnr_id', '=', tmpl_id), ('id', '!=', product.id)],
                                            context=context)
            if not other_product_ids:
                unlink_product_tmpl_ids.append(tmpl_id)
            unlink_ids.append(product.id)
        res = super(partner_application_form, self).unlink(cr, uid, unlink_ids, context=context)
        # delete templates after calling super, as deleting template could lead to deleting
        # products due to ondelete='cascade'
        self.pool.get('res.partner').unlink(cr, uid, unlink_product_tmpl_ids, context=context)
        return res

    # def create(self, cr, uid, vals, context={}):
    #     print "=========", uid,vals
    #     return super(partner_application_form, self).create(cr,SUPERUSER_ID, vals, context)


    def write(self, cr, uid, ids, vals, context=None):
        #         if self.browse(cr,uid,ids[0]).select_tin=='tin_menu':
        for data in self.browse(cr, uid, ids):
            if data.select_tin == 'tin_menu':
                if 'tin' in vals:
                    vals['select_tin'] = 'tin_vals'

            details = ""



        result = super(partner_application_form, self).write(cr, uid, ids, vals, context=context)
        return result

    # def app_form_to_profile(self,cr,uid,ids,context=None):



    def name_get(self, cr, uid, ids, context=None):

        vals = super(partner_application_form, self).name_get(cr, uid, ids, context)
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
        obj = self.browse(cr, uid, ids)
        cr.execute("select tin_prefix from tax_configuration")
        config_res = cr.fetchone()
        if not config_res:
            raise except_orm(_('No Configuration Found!'),
                             _("Please configure TIN Prefix Under Tax Configuration' !"))
        prefix = config_res and config_res[0] or ''
        randon_value = random.randint(0000001, 9999999)
        number = str(prefix) + str(randon_value)
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
        self.write(cr, uid, [ids[0]], {'generate_tin': True, 'select_tin': 'tin_menu', 'tin': number})
        return True

    def button_reject(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            if data.res_ptnr_id:
                self.pool.get('res.partner').write(cr, uid, [data.res_ptnr_id.id], {'approve_state': 'new'})

            if not data.reject:
                raise except_orm(_('No Configuration Found!'),
                                 _("Please Provide the reason for Rejection' !"))
            details=""

            subject = "Application is rejected"
            details += " <br/> For Reason : " + data.reject
            self.message_post(cr, uid, ids, body=details,
                                                                   subject=subject,
                                                                   limit=2, context=context)
            return self.write(cr, uid, ids, {'approve_state': 'rejected'}, context=context)

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
        details = ""

        subject = "Your Application is Approved"
        details += " <br/>"
        self.message_post(cr, uid, ids, body=details,
                          subject=subject,
                          limit=2, context=context)

        self.write(cr, uid, [ids[0]], {'application_state': 'approve', 'is_approve': True})
        return True

    def action_application_approve(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            if not data.tax_office_id:
                raise except_orm(_('No Configuration Found!'),
                                 _("Please Assign Tax Office Id for the Candidate' !"))
            if data.res_ptnr_id:
                self.pool.get('res.partner').write(cr, uid, [data.res_ptnr_id.id], {
                    'approve_state': 'approve', 'sex': data.sex, 'last_name': data.last_name,

                    'user_id': data.user_id and data.user_id.id, 'date_of_birth': data.date_of_birth,
                    'other_name': data.other_name,

                    'marital_state': data.marital_state, 'tax_config_id': data.tax_config_id and data.tax_config_id.id,
                    'property_income_receive': data.property_income_receive,
                    'dispose_of_chargeable_assets': data.dispose_of_chargeable_assets,

                    'interest_income_receive': data.interest_income_receive,
                    'dividend_income_receive': data.dividend_income_receive,
                    'over_income_receive': data.over_income_receive,
                    'pasb_income_receive': data.pasb_income_receive,
                    'origin_state_id': data.origin_state_id and data.origin_state_id.id,
                    'local_govt_city': data.local_govt_city,
                    'trade_name': data.trade_name,
                    'self_employed_business': data.self_employed_business,
                    'business_names': data.business_names,

                    'bvn': data.bvn,
                    'license_no': data.driver_license,
                    'national_id': data.national_id,})

            if data.user_id and data.application_type == 'self_employed':
                groups_obj = self.pool.get('res.groups')
                self_emp_grp_id = groups_obj.search(cr, uid, [
                    ('name', 'in', ['Self Employed', 'E-Tax Payer', 'Tax Accounting'])])
                groups_obj.write(cr, uid, self_emp_grp_id, {'users': [(4, data.user_id.id)], })
            if data.user_id and data.application_type == 'employed':
                groups_obj = self.pool.get('res.groups')
                self_emp_grp_id = groups_obj.search(cr, uid,
                                                    [('name', 'in', ['Employed', 'E-Tax Payer', 'Tax Accounting'])])
                groups_obj.write(cr, uid, self_emp_grp_id, {'users': [(4, data.user_id.id)], })
            if data.user_id and data.application_type == 'corporate':
                groups_obj = self.pool.get('res.groups')
                self_emp_grp_id = groups_obj.search(cr, uid,
                                                    [('name', 'in', ['Corporate', 'E-Tax Payer', 'Tax Accounting'])])
                groups_obj.write(cr, uid, self_emp_grp_id, {'users': [(4, data.user_id.id)], })
        return self.write(cr, uid, ids, {'approve_state': 'approve', 'is_approve': True}, context=context)

    def action_application_submit(self, cr, uid, ids, context=None):
        name = self.pool.get('ir.sequence').get(cr, uid, 'partner.application.form', context=context) or '/'
        for data in self.browse(cr, uid, ids):
            if data.res_ptnr_id:

                self.pool.get('res.partner').write(cr, uid, [data.res_ptnr_id.id], {'approve_state': 'review', 'number': data.id})
        details = ""
        subject = "Your Have Submitted your application"
        details += " <br/>"
        self.message_post(cr, uid, ids, body=details,
                          subject=subject,
                          limit=2, context=context)
        return self.write(cr, uid, ids, {'approve_state': 'review', 'is_approve': False, 'number': name}, context=context)

    def action_application_reject(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            if data.res_ptnr_id:
                self.pool.get('res.partner').write(cr, uid, [data.res_ptnr_id.id], {'approve_state': 'new'})
        return self.write(cr, uid, ids, {'approve_state': 'new', 'is_approve': False}, context=context)


# class etax_tax_office(osv.osv):
#     _name = 'etax.tax.office'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
#     _columns = {
#         'name': fields.char('Name of the tax office', required=True),
#         'city': fields.char('City', required=True),
#         'state_id': fields.many2one('res.country.state', 'State', required=True),
#     }

# class tax_configuration(osv.osv):
#     _name='tax.configuration'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
#     _columns={
#               'name':fields.char('Name',required=True),
#                'tin_prefix': fields.char('TIN Prefix', size=3),
#               'product':fields.many2one('product.product','Product'),
#               'assessment_charges_product':fields.many2one('product.product','Assesment Charges Product'),
#               'admin_charges_product':fields.many2one('product.product','Admin Charges Product'),
#               'assessment_charges':fields.float('Assessment Charges'),
#               'admin_charges':fields.float('Admin Charges'),
#               'companies_income_tax':fields.float('Companies Income Tax'),
#               'petroleurm_profit_tax':fields.float('Petroleum Profit Tax'),
#               'education_tax':fields.float('Education Tax'),
#               'technology_levy':fields.float('Technology Levy'),
#               'companies_income_product':fields.many2one('product.product','Companies Income Tax Product'),
#               'petroleurm_profit_product':fields.many2one('product.product','Petoleum Profit Tax Product'),
#               'education_tax_product':fields.many2one('product.product','Education Tax Product'),
#               'technology_levy_product':fields.many2one('product.product','Technology Levy Product'),
#               'account_tax_id':fields.many2many('account.tax','tax_configuration_account_rel','tax_configuration_id','account_tax_id',string="Other Taxes"),
#
#
#               }


# class etax_claim(osv.osv):
#     _name = 'etax.claim'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
#     _description = 'E-tax Claim'
#
#     _columns = {
#         'name': fields.char('Name'),
#         'state': fields.selection(
#             [('draft', 'New'), ('submit', 'Submit'), ('accept', 'Accept'), ('reject', 'Reject'), ('done', 'Done')],
#             'State', track_visibility='onchange'),
#         'submit_date': fields.datetime('Submit Date'),
#         'accept_date': fields.datetime('Accept Date'),
#         'reject_date': fields.datetime('Reject Date'),
#         'done_date': fields.datetime('Done Date'),
#         'partner_id': fields.many2one('res.partner', 'Profile'),
#         'user_id': fields.many2one('res.users', 'User'),
#         'tax_id': fields.many2one('tax.calculator.individual', 'Assessment Id'),
#
#     }
#
#     def _get_default_partner_id(self, cr, uid, context=None):
#         ids = self.pool.get('res.partner').search(cr, uid, [('user_id', '=', uid)], context=context)
#         partner_id = False
#         if ids:
#             partner_id = ids[0]
#         return partner_id
#
#     _defaults = {
#         'state': 'draft',
#         'user_id': lambda obj, cr, uid, context: uid,
#         'partner_id': _get_default_partner_id,
#         'tax_id': lambda obj, cr, uid, context: uid,
#
#     }
#
#     def action_submit(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids, {'state': 'submit', 'submit_date': time.strftime('%Y-%m-%d')}, context=context)
#
#     def action_accept(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids, {'state': 'accept', 'accept_date': time.strftime('%Y-%m-%d')}, context=context)
#
#     def action_reject(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids, {'state': 'reject', 'reject_date': time.strftime('%Y-%m-%d')}, context=context)
#
#     def action_done(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids, {'state': 'done', 'done_date': time.strftime('%Y-%m-%d')}, context=context)


