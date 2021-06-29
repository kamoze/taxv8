from openerp.osv import fields, osv
from openerp.tools.translate import _
import urllib2
import time
import datetime
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from openerp import api
from openerp import SUPERUSER_ID
from openerp.exceptions import except_orm


""" This file contains two models that is used to calculate the tax for corporate and individual tax """


class tax_calculator_corporate(osv.osv):
    _name = 'tax.calculator.corporate'

    def calculate_tax(self, cr, uid, ids, context=None):
        print"calllllllllllllllllllllllllll"

        res = {}
        for tax_id in self.browse(cr, uid, ids, context=context):
            a = tax_id.previous_revenue
            #             b = tax_id.income_unearned
            #             c = tax_id.statutory_reliefs
            #             d = tax_id.other_deductions
            t = tax_id.tax_rate

        #         gai = a + b
        #         tnti = c + d
        #         tti = gai - tnti
        atd = a * t
        res['annual_tax'] = atd
        mt = atd / 12.0
        res['monthly_tax'] = mt
        self.write(cr, uid, ids, res)
        return True

    def send_demand_notice(self, cr, uid, ids, context=None):
        text = ''
        for val in self.browse(cr, uid, ids):
            text = 'Total Amount-' + str(val.total_amount) + '\n' + 'Tax Liability-' + str(
                val.tax_liability) + '\n' + 'Consolidated Relief-' + str(
                val.consolidated_relief_one) + '\n' + 'Total Relief-' + str(
                val.total_relief) + '\n' + 'Net Taxable Income-' + str(val.net_taxable_income)
            url = 'http://api.infobip.com/api/v3/sendsms/plain?user=spanbox&password=cyini74&sender=DELTA_TAX&SMSText=' + str(
                urllib2.quote(text)) + '&GSM=' + str(val.name.mobile)
            response = urllib2.urlopen(url)
            print'json_response===', response
        return True

    def send_demand_notic_mail(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        email_template_obj = self.pool.get('email.template')
        template_ids = ir_model_data.get_object_reference(cr, uid, 'etax', 'send_mail_tax_cotrporate_calculator')[1]
        details = ""

        subject = "Assesment Demand Notice Mail Sended"
        details += " <br/> For Notice By : " + uid
        self.message_post(cr, uid, ids, body=details,
                          subject=subject,
                          limit=2, context=context)
        try:
            compose_form_id = \
                ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'res.partner',
            'default_res_id': ids[0],
            'default_use_template': bool(template_ids),
            'default_template_id': template_ids,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })

    def send_email_to_admin(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'tax', 'email_template_edi_tax')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[
                1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'tax.calculator.corporate',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
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

    def _total_amount(self, cr, uid, ids, name, args, context=None):
        res = {}

        for val in self.browse(cr, uid, ids):
            self_employed = val.trading_profit + val.buisness_income + val.other_profits + val.professional_income
            # print "self_employed===============",self_employed
            paid_employment = val.salary + val.commission + val.bonuses + val.gratuties + val.fees + val.benefits_in_kind + val.other_income
            # print "paid_employment=============",paid_employment
            unearned_income = val.dividends + val.interest + val.rent + val.royalities + val.others
            # print "unearned_income=============",unearned_income
            res[val.id] = self_employed + paid_employment + unearned_income
            print res
        return res

    def _consolidated_relief(self, cr, uid, ids, name, args, context=None):
        res = {}
        ta1 = 0.0
        for val in self.browse(cr, uid, ids):
            ta = val.total_amount - (val.dividends + val.interest)
            if ta > 300000:
                if ta > 200000:
                    ta1 = ta * 0.01
                else:
                    ta1 = 200000
                print "ta1=========**=", ta1
            else:
                ta1 = ta * 0.01
            res[val.id] = ta1
            print res
        return res

    def _total_relief(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            total_statutory_deduction = val.gratuities + val.pensions_contributions + val.nhf_contributions + val.ins_superannuations + val.nhis_contributions + val.mortgage_interest + val.subuscription + val.life_assurance_relif + val.capital_allowances + val.balancing_charges + val.balancing_allowaces + val.losses
            print "total_statutory_deduction=====", total_statutory_deduction
            res[val.id] = val.consolidated_relief_one + total_statutory_deduction
            print res
        return res

    def _net_taxable_income(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            gross_income = val.dividends + val.interest + val.rent + val.royalities + val.others
            taxable_income = val.total_amount - val.total_relief
            res[val.id] = taxable_income - (val.dividends + val.interest)
            print res
        return res

    def _tax_liability(self, cr, uid, ids, name, args, context=None):
        res = {}
        tax_liability = 0.0
        for val in self.browse(cr, uid, ids):
            if val.total_amount > 0 and val.total_amount < 300000:
                taxable_income = val.total_amount
                tax_liability = 0.01 * taxable_income
            elif val.total_amount > 300000 and val.total_amount < 600000:
                tax_liability = 21000 + 0.11 * (val.total_amount - 300000)
            elif val.total_amount > 600000 and val.total_amount < 1100000:
                tax_liability = 54000 + 0.15 * (val.total_amount - 600000)
            elif val.total_amount > 1100000 and val.total_amount < 1600000:
                tax_liability = 129000 + 0.19 * (val.total_amount - 1100000)
            elif val.total_amount > 1600000 and val.total_amount < 3200000:
                tax_liability = 224000 + 0.21 * (val.total_amount - 1600000)
            elif val.total_amount > 3200000:
                tax_liability = 560000 + 0.24 * (val.total_amount - 3200000)

            res[val.id] = tax_liability
            print res
        return res

    _columns = {
        'trading_profit': fields.float('Trading Profit'),
        'buisness_income': fields.float('Business Income'),
        'other_profits': fields.float('Other Profits'),
        'professional_income': fields.float('Professional/Vocational Income'),
        'salary': fields.float('Salary'),
        'commission': fields.float('Commission'),
        'bonuses': fields.float('Bonuses'),
        'gratuties': fields.float('Gratuties'),
        'fees': fields.float('Fees'),
        'benefits_in_kind': fields.float('Benefits In Kind'),
        'other_income': fields.float('Other Income'),
        'dividends': fields.float('Dividends(Gross)'),
        'interest': fields.float('Interest(Gross)'),
        'rent': fields.float('Rent(Gross)'),
        'royalities': fields.float('Royalities(Gross)'),
        'others': fields.float('Other(Gross)'),
        'gratuities': fields.float('Gratuities'),
        'pensions_contributions': fields.float('Pensions Contributions'),
        'nhf_contributions': fields.float('NHF Contributions'),
        'ins_superannuations': fields.float('INS Superannuations'),
        'nhis_contributions': fields.float('NHIS Contributions'),
        'mortgage_interest': fields.float('Mortgage Interest'),
        'subuscription': fields.float('Subscription To Professional Body'),
        'life_assurance_relif': fields.float('Life Assurance Relif'),
        'capital_allowances': fields.float('Capital_Allowances'),
        'balancing_charges': fields.float('Balancing Charges'),
        'balancing_allowaces': fields.float('Balancing Allowaces'),
        'losses': fields.float('Losses'),

        'total_amount': fields.function(_total_amount, type='float', string="Total Amount"),
        'consolidated_relief_one': fields.function(_consolidated_relief, type='float', string="Consolidated Relief"),
        'total_relief': fields.function(_total_relief, type='float', string="Total Relief"),
        'net_taxable_income': fields.function(_net_taxable_income, type='float', string="Net Taxable Income"),
        'tax_liability': fields.function(_tax_liability, type='float', string='Tax Liability'),
        'name': fields.many2one('res.partner', 'Name of the Company',
                                domain="[('is_company','=',True),('e_tax','=',True)]", required=True),
        'company_street': fields.char('Address'),
        'company_street2': fields.char(' '),
        'company_city': fields.char(' '),
        'company_state_id': fields.many2one('res.country.state', ' '),
        'company_zip': fields.char(' '),
        'company_country_id': fields.many2one('res.country', ' '),
        'incorp_ref_no': fields.char('Incorporate Reference Number'),
        'date': fields.date('Date'),
        'tin_no': fields.char('TIN', help='Tax Identification Number', required=True),
        'business_nature': fields.char('Business', help='Nature of Trade/Business'),
        'previous_turnover': fields.float('Turnover', help="Previous year's annual turnover", required=True),
        'previous_revenue': fields.float('Revenue', help="Previous year's annual revenue", required=True),
        'previous_tax_certificate': fields.char('Certificate Number', help='Previous Tax Clearance Certificate No.'),
        'previous_tax_paid': fields.boolean('Assessment Paid?', help='Previous Year Assessment paid up to date'),
        'liquadation_concession_arranged': fields.boolean('Concession Required?',
                                                          help='Concession arranged for liquadation'),
        'tax_rate': fields.float('Tax rate', required=True),
        'annual_tax': fields.float(string='Annual Tax', readonly=True),
        'monthly_tax': fields.float(string='Monthly Tax', readonly=True),
    }

    def onchange_company(self, cr, uid, ids, name, context=None):
        v = {}
        if name:
            company_obj = self.pool.get('res.partner').browse(cr, uid, name)
            v['company_street'] = company_obj.street
            v['company_street2'] = company_obj.street2
            v['company_city'] = company_obj.city
            v['company_state_id'] = company_obj.state_id.id
            v['company_zip'] = company_obj.zip
            v['company_country_id'] = company_obj.country_id.id
            v['tin_no'] = company_obj.vat

        return {'value': v}


class tax_calculator_individual(osv.osv):
    _name = 'tax.calculator.individual'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    #


    def calculate_tax(self, cr, uid, ids, context=None):
        res = {}
        for tax_id in self.browse(cr, uid, ids, context=context):
            a = tax_id.income_earned
            b = tax_id.income_unearned
            c = tax_id.statutory_reliefs
            d = tax_id.other_deductions
            t = tax_id.tax_rate

        gai = a + b
        tnti = c + d
        tti = gai - tnti
        atd = t * tti
        res['annual_tax'] = atd
        mt = atd / 12
        res['monthly_tax'] = mt
        self.write(cr, uid, ids, res)
        return True

    def send_demand_notic_mail(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        email_template_obj = self.pool.get('email.template')
        individual_tax = self.browse(cr, uid, ids[0])
        template_ids = ir_model_data.get_object_reference(cr, uid, 'etax', 'send_mail_tax_calculator')[1]
        try:
            compose_form_id = \
                ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'res.partner',
            'default_res_id': ids[0],
            'default_use_template': bool(template_ids),
            'default_template_id': template_ids,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_partner_ids': individual_tax.name.ids
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

    def send_demand_notice(self, cr, uid, ids, context=None):
        text = ''
        for val in self.browse(cr, uid, ids):
            text = 'Total Amount-' + str(val.total_amount) + '\n' + 'Tax Liability-' + str(
                val.tax_liability) + '\n' + 'Consolidated Relief-' + str(
                val.consolidated_relief_one) + '\n' + 'Total Relief-' + str(
                val.total_relief) + '\n' + 'Net Taxable Income-' + str(val.net_taxable_income)
            url = 'http://api.infobip.com/api/v3/sendsms/plain?user=spanbox&password=cyini74&sender=DELTA_TAX&SMSText=' + str(
                urllib2.quote(text)) + '&GSM=' + str(val.name.mobile)
            response = urllib2.urlopen(url)
        return True
        # create_invoice_line_id=inv_line_obj(cr,uid,{'name':val.product_id,})

    def _total_amount(self, cr, uid, ids, name, args, context=None):
        res = {}

        for val in self.browse(cr, uid, ids):
            self_employed = val.trading_profit + val.buisness_income + val.other_profits + val.professional_income
            # print "self_employed===============", self_employed
            paid_employment = val.salary + val.commission + val.bonuses + val.gratuties + val.fees + val.benefits_in_kind + val.other_income
            # print "paid_employment=============", paid_employment
            unearned_income = val.dividends + val.interest + val.rent + val.royalities + val.others
            # print "unearned_income=============", unearned_income
            res[val.id] = self_employed + paid_employment + unearned_income
            print res
        return res

    def _consolidated_relief(self, cr, uid, ids, name, args, context=None):
        res = {}
        ta1 = 0.0
        per= 0.0
        tota2 = 0.0
        ta =0.0
        for val in self.browse(cr, uid, ids):
            ta = val.total_amount - (val.dividends + val.interest)

            if val.total_amount<= 250000:
                ta1 = 0

            elif val.total_amount > 250000:

                per = ta* .01
                tota2 = ta * 0.2
                if  per < 200000:
                    ta1 = 200000 + tota2
                else:
                    ta1 = per + tota2
            res[val.id] = ta1
            print res
        return res

    def _total_relief(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            cr2 = 0.0
            ta = val.total_amount - (val.dividends + val.interest)
            #total_statutory_deduction = val.gratuities + val.pensions_contributions + val.nhf_contributions + val.ins_superannuations + val.nhis_contributions + val.mortgage_interest + val.subuscription + val.life_assurance_relif + val.capital_allowances + val.balancing_charges + val.balancing_allowaces + val.losses
            total_statutory_deduction = val.gratuities + val.pensions_contributions + val.nhf_contributions + val.ins_superannuations + val.nhis_contributions + val.mortgage_interest + val.subuscription + val.life_assurance_relif + val.capital_allowances + val.balancing_charges + val.balancing_allowaces + val.losses

            print "total_statutory_deduction=====", total_statutory_deduction
            if ta < 250000:
                cr2 = 0
            else:
                cr2 = val.consolidated_relief_one + total_statutory_deduction
            res[val.id] =  cr2
            print res
        return res

    def _net_taxable_income(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            total_statutory_deduction = val.gratuities + val.pensions_contributions + val.nhf_contributions + val.ins_superannuations + val.nhis_contributions + val.mortgage_interest + val.subuscription + val.life_assurance_relif + val.capital_allowances + val.balancing_charges + val.balancing_allowaces + val.losses

            taxable_income = val.taxable_income
            res[val.id] = val.total_amount - val.total_relief
            print res
        return res


    def _taxable_income(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            total_statutory_deduction = val.gratuities + val.pensions_contributions + val.nhf_contributions + val.ins_superannuations + val.nhis_contributions + val.mortgage_interest + val.subuscription + val.life_assurance_relif + val.capital_allowances + val.balancing_charges + val.balancing_allowaces + val.losses

            taxable_income = val.total_amount - val.total_relief
            res[val.id] = taxable_income
            print res
        return res


    def _tax_liability(self, cr, uid, ids, name, args, context=None):
        res = {}
        tax_liability = 0.0
        for val in self.browse(cr, uid, ids):
            if val.net_taxable_income < 0.0:
                val.net_taxable_income = 0.0

            elif val.total_amount > 0 and val.total_amount <= 300000:
                taxable_income = val.total_amount
                tax_liability = 0.01 * taxable_income
            # elif val.total_amount > 300000 and val.total_amount <= 600000:
            #     taxable_income = val.net_taxable_income
            #     tax_liability = 0.07 * taxable_income


            elif val.net_taxable_income > 0 and val.net_taxable_income <= 300000:
                taxable_income = val.net_taxable_income
                tax_liability = 0.07 * taxable_income
            # elif val.net_taxable > 0 and val.net_taxable <= 300000:
            #
            #     tax_liability = 21000 + 0.11 * (val.net_taxable - 300000)
            elif val.net_taxable_income > 300000 and val.net_taxable_income <= 600000:
                 tax_liability = 21000 + 0.11 * (val.net_taxable_income - 300000)
            elif val.net_taxable_income > 600000 and val.net_taxable_income <= 1100000:
                tax_liability = 54000 + 0.15 * (val.net_taxable_income - 600000)
            elif val.net_taxable_income > 1100000 and val.net_taxable_income <= 1600000:
                tax_liability = 129000 + 0.19 * (val.net_taxable_income - 1100000)
            elif val.net_taxable_income > 1600000 and val.net_taxable_income <= 3200000:
                tax_liability = 224000 + 0.21 * (val.net_taxable_income - 1600000)
            elif val.net_taxable_income > 3200000:
                tax_liability = 560000 + 0.24 * (val.net_taxable_income - 3200000)
            res[val.id] = tax_liability
            val.write({'annual_tax': tax_liability, 'monthly_tax': tax_liability / 12.0})
        return res

    def _get_default_partner_id(self, cr, uid, context=None):
        partner = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
        return partner

    _columns = {
        'name1': fields.char('No.'),
        'trading_profit': fields.float('Trading Profit'),
        'buisness_income': fields.float('Business Income'),
        'other_profits': fields.float('Other Profits'),
        'professional_income': fields.float('Professional/Vocational Income'),
        'salary': fields.float('Salary'),
        'commission': fields.float('Commission'),
        'bonuses': fields.float('Bonuses'),
        'gratuties': fields.float('Gratuties'),
        'fees': fields.float('Fees'),
        'benefits_in_kind': fields.float('Benefits In Kind'),
        'other_income': fields.float('Other Income'),
        'dividends': fields.float('Dividends(Gross)'),
        'interest': fields.float('Interest(Gross)'),
        'rent': fields.float('Rent(Gross)'),
        'royalities': fields.float('Royalities(Gross)'),
        'others': fields.float('Other(Gross)'),
        'gratuities': fields.float('Gratuities'),
        'pensions_contributions': fields.float('Pensions Contributions'),
        'nhf_contributions': fields.float('NHF Contributions'),
        'ins_superannuations': fields.float('INS Superannuations'),
        'nhis_contributions': fields.float('NHIS Contributions'),
        'mortgage_interest': fields.float('Mortgage Interest'),
        'subuscription': fields.float('Subscription To Professional Body'),
        'life_assurance_relif': fields.float('Life Assurance Relif'),
        'capital_allowances': fields.float('Capital_Allowances'),
        'balancing_charges': fields.float('Balancing Charges'),
        'balancing_allowaces': fields.float('Balancing Allowaces'),
        'losses': fields.float('Losses'),
        'total_amount': fields.function(_total_amount, type='float', string="Total Income"),
        'consolidated_relief_one': fields.function(_consolidated_relief, type='float', string="Consolidated Relief"),
        'total_relief': fields.function(_total_relief, type='float', string="Total Relief"),
        'net_taxable_income': fields.function(_net_taxable_income, type='float', string="Net Taxable Income"),
        'net_taxable': fields.function(_taxable_income, type='float', string="Net Taxable Income"),
        'taxable_income': fields.function(_taxable_income, type='float', string="Taxable Income"),

        'tax_liability': fields.function(_tax_liability, type='float', string='Tax Liability'),
        'name': fields.many2one('res.partner', 'Name',
                                domain="[('e_tax','=',True),'|',('is_employed','=',True),('is_self_employed','=',True)]",
                                required=True),
        'income_earned': fields.float('Earned Income'),
        'income_unearned': fields.float('Unearned Income'),
        'statutory_reliefs': fields.float('Statutory Reliefs'),
        'other_deductions': fields.float('Other Deduction'),
        'tax_rate': fields.float('Tax rate'),
        'annual_tax': fields.float(string='Annual Tax', readonly=True),
        'monthly_tax': fields.float(string='Monthly Tax', readonly=True),
        'state': fields.selection(
            [('draft', 'New',), ('submit', 'Submit'), ('confirm', 'Re-Assessment'),
             ('done', 'Done'), ('invoice', 'Invoice'), ('paid', 'Paid'),('cancel', 'Cancel')], 'State', track_visibility='onchange'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'submit_date': fields.date('Submit Date'),
        'confirm_date': fields.date('Confirm Date'),
        'done_date': fields.date('Done Date'),
        'reassesment_date': fields.date('Re Assessment Date'),
        'invoice_date': fields.date('Invoice Date'),
        'payment_date': fields.date('Payment Date'),
        'cancel_date': fields.date('Cancel Date'),
        # 'relevant tax':fields.float('Relevant Tax'),
        'assessment_charges_product': fields.many2one('product.product', 'Assesment Charges Product'),
        'assessment_charges': fields.float('Assessment Charges'),
        'admin_charges_product': fields.many2one('product.product', 'Admin Charges Product'),
        'admin_charges': fields.float('Admin Charges'),
        'user_id': fields.many2one('res.users', 'User Id'),
        'type_tax': fields.selection(
            [('corporate', 'Corporate'), ('employed', 'Employed'), ('self_employed', 'Self Employed')], 'Type Tax'),
        'street': fields.char('Address'),
        'number': fields.char('Number'),

        'assesment_number': fields.char('Assesment Number'),

        'tax_office_id': fields.many2one('etax.tax.office', ' Tax Office'),
        'tax_config_id': fields.many2one('tax.configuration', "Tax Configuration Id"),



    }

    _defaults = {
        'state': 'draft',
        'name': False,
        'user_id': lambda obj, cr, uid, context: uid,

        # 'name': lambda obj, cr, uid, context: obj.pool.get('res.users').browse(cr, uid, uid ).partner_id.id,
    }

    # @api.model
    # def write(self, vals):
    #     vals['']
    #     return super(tax_calculator_individual, self).write(vals)

    def create(self, cr, uid, vals, context=None):
        # print"vals createeeeeeeeeeeeee.........", vals
        #         res = {}
        #         res1={}
        #         current_year=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        #         present_year=datetime.strptime(str(current_year),"%Y-%m-%d").strftime("%y")
        #         print"current_date============",present_year
        obj_name = self.pool.get('res.partner').browse(cr, uid, vals['name'])
        #         print "obj_name=======================",obj_name
        #         print "vals==================",obj_name.name.upper(),obj_name.last_name,obj_name.other_name,obj_name.tax_config_id.admin_charges
        #
        #         if 'name' in vals:
        #              if obj_name.name and obj_name.last_name:
        #                   fullname= obj_name.name.upper()[0:1]+ obj_name.last_name.upper()[0:1]
        #              elif obj_name.name and obj_name.last_name:
        #                   fullname=obj_name.name.upper()[0:1] + obj_name.last_name.upper()[0:1]
        #              else:
        #                  fullname=obj_name.name.upper()[0:1]
        #              print"fullname================================",fullname
        #
        #         vals['name1'] = self.pool.get('ir.sequence').get(cr, uid, 'tax.calculator.individual') or '/'
        #         res1=vals['name1']+fullname+present_year
        #         print "res1=========",res1,obj_name.tax_config_id.admin_charges
        #         vals['name1']=res1
        if obj_name.tax_office_id and obj_name.tax_office_id.tax_config_id:
            object = obj_name.tax_office_id.tax_config_id
            vals['admin_charges'] = object.admin_charges
            vals['assessment_charges'] = object.assessment_charges
            vals[
                'admin_charges_product'] = object.admin_charges_product and object.admin_charges_product.id or False
            if object.assessment_charges_product:
                vals['assessment_charges_product'] = object.assessment_charges_product.id

        res = super(tax_calculator_individual, self).create(cr, uid, vals, context=context)

        return res

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.tax_office_id = self.name.tax_office_id and self.name.tax_office_id.id


    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    @api.multi
    def action_submit(self):
        follower_ids = []
        name = self.env['ir.sequence'].next_by_code('tax.calculator')
        self.assesment_number = name

        group_id = self.env['res.groups'].sudo().search([('name','=','E-Tax Officer')])
        if group_id:
            for part in group_id.users:
                follower_ids.append(part.partner_id.id)
        if follower_ids:
            self.message_subscribe(partner_ids=follower_ids)

        self.message_post(
            body="New Request for Assessment approval has been submitted by %s. Please login see the application and take necessary Action(if required)" % self.name.name,
            message_type='email', subject="Request for Assessment Approval from %s" % (self.name.name), )
        self.write({'state': 'submit', 'submit_date': time.strftime('%Y-%m-%d')})


        #         mail_mail=self.pool.get('mail.mail')
        #                     # the invite wizard should create a private message not related to any object -> no model, no res_id
        #         mail_id = mail_mail.create(cr, uid, {
        #                         'model': 'tax.calculator.individual',
        #                         'res_id': ids[0],
        #                         'subject': 'Please Approve the Tax ',# 'Invitation to follow %s' % document.name_get()[0][1],
        #                         'body_html':'taxpayer submit the tax.' ,
        #                         'auto_delete': False,
        #                         }, context=context)
        #         print "mai_id================",mail_id
        #         mail_mail.send(cr, uid, [mail_id], recipient_ids=[self.browse(cr,uid,ids[0]).name.id], context=context)
        #         return obj
        # assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        # ir_model_data = self.pool.get('ir.model.data')
        # try:
        #     template_id = ir_model_data.get_object_reference(cr, uid, 'tax', 'email_template_edi_tax')[1]
        # except ValueError:
        #     template_id = False
        # try:
        #     compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[
        #         1]
        # except ValueError:
        #     compose_form_id = False
        # ctx = dict(context)
        # ctx.update({
        #     'default_model': 'tax.calculator.individual',
        #     'default_res_id': ids[0],
        #     'default_use_template': bool(template_id),
        #     'default_template_id': template_id,
        #     'default_composition_mode': 'comment',
        #     'mark_invoice_as_sent': True,
        # })
        return True
        # {
        # 'type': 'ir.actions.act_window',
        # 'view_type': 'form',
        # 'view_mode': 'form',
        # 'res_model': 'mail.compose.message',
        # 'views': [(compose_form_id, 'form')],
        # 'view_id': compose_form_id,
        # 'target': 'new',
        # 'context': ctx,
        # }

    @api.multi
    def action_confirm(self):
        self.message_post(
            body="Assement request Submitted by %s has been approved. Please login see the application and take necessary Action(if required)" % self.name.name,
            message_type='email', subject="Assessment Confirmation for %s" % (self.name.name), )

        return self.write({'state': 'confirm', 'confirm_date': time.strftime('%Y-%m-%d')})
        # mail_mail = self.pool.get('mail.mail')
        # the invite wizard should create a private message not related to any object -> no model, no res_id
        # mail_id = mail_mail.create(cr, uid, {
        #     'model': 'tax.calculator.individual',
        #     'res_id': ids[0],
        #     'subject': 'sorry,assessment is disapprove. Try to reassesment between 7days. ',
        # 'Invitation to follow %s' % document.name_get()[0][1],
            # 'body_html': 'Tax Admin disapprove the tax',
            # 'auto_delete': False,
        # }, context=context)
        # mail_browse = mail_mail.browse(cr, uid, ids, context=context)
        # for r_id in mail_browse.ids:
        #     if r_id:
        #         mail_mail.send(mail_mail, cr, uid, [mail_id],
        #         mail.recipient_ids=([self.browse(cr,uid,ids[0]).name.id], context=context):
                # return obj

    @api.multi

    def action_reassessment(self):
        self.message_post(
            body="Assessment form New by %s has been completed.)" % self.state,
            message_type='email', subject="Assessment completed for %s" % (self.name.name), )
        return self.write( {'state': 'draft', 'reassesment_date': time.strftime('%Y-%m-%d')},
                          )
    @api.multi
    def action_done(self):
        self.message_post(
            body="Assessment form submitted by %s has been completed. Please login see the application and take necessary Action(if required)" % self.name.name,
            message_type='email', subject="Assessment completed for %s" % (self.name.name), )
        return self.write({'state': 'done', 'done_date': time.strftime('%Y-%m-%d')})

    def action_cancel(self, cr, uid, ids, context=None):
        self.message_post(
            body="Assessment form Cancelled by %s has been completed. Please login see the application and take necessary Action(if required)" % self.name.name,
            message_type='email', subject="Assessment completed for %s" % (self.name.name), )
        return self.write(cr, uid, ids, {'state': 'cancel', 'cancel_date': time.strftime('%Y-%m-%d')}, context=context)

    def action_reset(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})

    def tax_configuration(self, cr, uid, ids, context=None):
        obj_tax_calc = self.pool.get('tax.calculator.individual')
        for val in self.browse(cr, uid, ids):
            create_id = obj_tax_calc.create(cr, uid, {'admin_charges1', val.name.tax_config_id.admin_charges})

    def create_invoice(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')])

        for val in self.browse(cr, uid, ids):
            invoice_id = False
            tax_config = val.tax_office_id and val.tax_office_id.tax_config_id#name.tax_office_id and val.name.tax_office_id.tax_config_id
            if not tax_config:
                raise osv.except_osv(_('Warning!'),
                        _("Tax Configuration Missing for %s Please configure first" % val.name.name))

            if not tax_config.product:
                raise osv.except_osv(_('Warning!'),
                                     _("Product Not Found Under Tax Configuration %s " % tax_config.name))

            invoice_dict =  {'partner_id': val.name.id,
                                                 'account_id': val.name.property_account_receivable.id,
                                                 'journal_id': journal_id[0],
                                                 'user_id': val.user_id and val.user_id.id,
                                                 'currency_id': self.pool.get('res.users').browse(cr, uid,
                                                                                                  uid).company_id.currency_id.id}
            # print"=-=-=-=-=-=-", create_id
            # product_id = self.pool.get('product.product').search(cr, uid, [('type', '=', 'service')])
            # print "product_id============", product_id
            line_ids = []
            tax_ids = [tx.id for tx in tax_config.account_tax_id]
            if tax_config.product:
                line_ids.append((0,0,{'product_id': tax_config.product.id,
                                    'name': tax_config.product.name,
                                    'quantity': 1, 'price_unit': val.tax_liability,
                                    'invoice_line_tax_id': [(6,0,tax_ids)]}))
            if tax_config.assessment_charges_product and tax_config.assessment_charges:
                line_ids.append((0, 0, {'product_id': tax_config.assessment_charges_product.id,
                                        'name': tax_config.assessment_charges_product.name,
                                        'quantity': 1, 'price_unit': tax_config.assessment_charges,
                                        'invoice_line_tax_id': [(6, 0, tax_ids)]}))
            if tax_config.admin_charges_product and tax_config.admin_charges:
                line_ids.append((0, 0, {'product_id': tax_config.admin_charges_product.id,
                                        'name': tax_config.admin_charges_product.name,
                                        'quantity': 1, 'price_unit': tax_config.admin_charges,
                                        'invoice_line_tax_id': [(6, 0, tax_ids)]}))
            if line_ids:
                invoice_dict['invoice_line'] = line_ids
                invoice_id = inv_obj.create(cr, uid, invoice_dict)
                inv_obj.signal_workflow(cr, uid, [invoice_id], 'invoice_open')
            self.write(cr, uid, [val.id],
                       {'state': 'invoice', 'invoice_id': invoice_id, 'invoice_date': time.strftime('%Y-%m-%d')},
                       context=context)
            self.message_post(cr, uid, [val.id],
                body="Invoice for Assessment submitted by %s has been created with Reference %s. Please login see the status and take necessary Action(if required)" % (val.name.name, val.invoice_id.number) ,
                message_type='email', subject="Invoice Created for %s" % (val.name.name), )

        return True

    def schedule_reassessment(self, cr, uid, ids, context=None):
        tax_cal_obj = self.pool.get('tax.calculator.individual')
        lst = tax_cal_obj.search(cr, uid, [('state', '=', 'reassesment')])
        if lst:
            current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            today_date = datetime.strptime(str(today_date), "%Y-%m-%d").strftime("%Y-%d-%m")
            for val in tax_cal_obj.browse(cr, uid, lst):
                day = 0
                tm_tuple = datetime.strptime(str(today_date), '%Y-%m-%d').timetuple()
                reassessment_date = datetime.strptime(str(val.reassesment_date), "%Y-%m-%d").strftime("%Y-%m-%d")
                tm_tuple1 = datetime.strptime(str(reassesment_date), '%Y-%d-%m').timetuple()
                day = int(tm_tuple1.tm_mday) - int(tm_tuple.tm_mday)
                if int(day) >= 7:
                    tax_cal_obj.action_cancel(cr, uid, [val.id], context=None)

        return True

    def create_sol(self, cr, uid, ids, context=None):
        #        print"a2"
        if not context:
            context = {}
        sline_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            return {
                'name': 'Tax Calculator Reassessment',
                'res_model': 'tax.calculator.reassesment',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'nodestroy': True,
                'context': dict(context, active_ids=ids)
            }

    def generate_invoice(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            return {
                'name': 'Generate Invoice',
                'res_model': 'generate.invoice',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'nodestoery': True,
                'context': dict(context, active_ids=ids)
            }

    def onchange_is_partner(self, cr, uid, ids, name, context=None):
        v = {}
        partner = self.pool.get('res.partner').browse(cr, uid, name)
        if name:
            v['number'] = partner.number
            v['tax_config_id'] = partner.tax_config_id.id
        return {'value': v}


class tax_certificate(osv.osv):
    _name = 'tax.certificate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_default_partner_id(self, cr, uid, context=None):
        partner = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
        return partner

    _columns = {
        'name': fields.char('Name'),
        'date': fields.date('Date'),
        'req_date': fields.datetime('Req Certificate Date', readonly=True),
        'lib_pending_date': fields.datetime('Liablity Pending Date', readonly=True),
        'lib_approve_date': fields.datetime('Liablity Approve Date', readonly=True),
        'acc_pending_date': fields.datetime('Account Pending Date', readonly=True),
        'acc_approve_date': fields.datetime('Account Approve Date', readonly=True),
        'certificate_date': fields.datetime('Certificate Date', readonly=True),
        'reject_date': fields.datetime('Reject Date', readonly=True),
        'state': fields.selection([('new', 'Draft'),
                                   ('req_certificate', 'Required Certificate'),
                                   ('lib_pending', 'Liablity Pending'),
                                   ('lib_approve', 'Liablity Approved'),
                                   ('account_pending', 'Account Pending'),
                                   ('account_approve', 'Account Approved'),
                                   ('certificate', 'Certificate Print'),
                                   ('reject', 'Reject'),
                                   ('close', 'Done')],
                                  'State', ),
        'user_id': fields.many2one('res.users', 'Person UID'),
        'partner_id': fields.many2one('res.partner', 'Profile'),
        'tax_cal_id': fields.many2one('tax.calculator.individual', 'Tax ID'),
        'certicate_approve': fields.text('Approve Remark'),
        'certicate_liability': fields.text('Liability Remark'),
        'certicate_print': fields.text('Print Remark'),
    }
    _defaults = {
        'state': 'new',
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_id': _get_default_partner_id,
    }

    @api.model
    def create(self, vals):
        res = super(tax_certificate, self).create(vals)
        res.message_post(
            body="%s Requested a New Tax Certification. Please login see and take necessary Action(if required)" % res.user_id.name,
            message_type='email', subject="New Tax Certificate Request '%s' from %s" % (res.name, res.user_id.name), )
        return res

    def _get_default_partner_id(self, cr, uid, context=None):
        partner = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
        return partner

    @api.multi
    def action_cer_new(self):
        self.message_post(
            body="%s Requested a New Tax Certification. Please login see and take necessary Action(if required)" % self.user_id.name,
            message_type='email', subject="New Tax Certificate Request '%s' from %s" % (self.name, self.user_id.name), )
        obj = self.write({'state': 'req_certificate', 'req_date': time.strftime('%Y-%m-%d')})
        return True

    @api.multi
    def action_certificate_new(self):
        self.message_post(
            body="%s Requested a New Tax Certification. Please login see and take necessary Action(if required)" % self.user_id.name,
            message_type='email', subject="New Tax Certificate Request '%s' from %s" % (self.name, self.user_id.name), )
        return self.write({'state': 'lib_pending', 'lib_pending_date': time.strftime('%Y-%m-%d')})

    @api.multi
    def action_lib_pending(self):
        self.write({'state': 'reject'})
        return True

    @api.multi
    def action_lib_approve(self):
        if not self.certicate_liability:
            raise except_orm(_('No Configuration Found!'),
                             _("Please Provide the Remark for Approve' !"))
        self.message_post(
            body="Certificate Liability Approve For Reason %s " % self.certicate_liability,
            message_type='email', subject="New Tax Certificate Request  Approve By %s" % (self.user_id.name), )
        return self.write({'state': 'lib_approve', 'lib_approve_date': time.strftime('%Y-%m-%d')})

    @api.multi
    def action_acc_pending(self):
        return self.write({'state': 'account_pending', 'acc_pending_date': time.strftime('%Y-%m-%d')})

    @api.multi
    def action_acc_approve(self):
        if not self.certicate_approve:

            raise except_orm(_('No Configuration Found!'),
                             _("Please Provide the Remark for Approve' !"))
        self.message_post(
            body="Certificate Approve For Reason %s " % self.certicate_approve,
            message_type='email', subject="Tax Certificate Liability Request  Approve By %s" % (self.user_id.name))
        return self.write({'state': 'account_approve', 'acc_approve_date': time.strftime('%Y-%m-%d')})

    @api.multi
    def action_certificate_done(self):
        if not self.certicate_print:
            raise except_orm(_('No Configuration Found!'),
                             _("Please Provide the Remark for Approve' !"))
        self.message_post(
            body="Certificate Print For Reason %s" % self.certicate_print,
            message_type='email', subject="Tax Certificate Request  Printed By %s" % (self.user_id.name), )
        return self.write({'state': 'certificate', 'certificate_date': time.strftime('%Y-%m-%d')})

    def action_close(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'close'}, context=context)
        return obj


class corporate_tax(osv.osv):
    _name = 'corporate.tax'
    _columns = {
        'name': fields.char('Name'),
        'date': fields.datetime('Date'),
        'confirm_date': fields.datetime('Confirm Date'),
        'tax_review_date': fields.datetime('Tax Review Date'),
        'approve_review_date': fields.datetime('Approve Review Date'),
        'claim_initiate_date': fields.datetime('Claim Initiate Date'),
        'invoice_initiate_date': fields.datetime('Invoice Initiate Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'partner_id': fields.many2one('res.partner', 'Profile'),
        'state': fields.selection([('new', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('tax_review', 'Tax Review'),
                                   ('approve_review', 'Approve Review'),
                                   ('claim_initiate', 'Claim Initiate'),
                                   ('invoice_initiate', 'Invoice Initiate'),
                                   ('close', 'Close')],
                                  'State', readonly=True),
    }

    _defaults = {
        'state': 'new',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def action_confirm_co(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'confirm', 'confirm_date': time.strftime('%Y-%m-%d')}, context=context)
        return obj

    def action_tax_review(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'tax_review', 'tax_review_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_approve_review(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'approve_review', 'approve_review_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_claim_initiate(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'claim_initiate', 'claim_initiate_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_invoice_initiate(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids,
                         {'state': 'invoice_initiate', 'invoice_initiate_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_close_co(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'close',}, context=context)
        return obj


class taxpayer_payment(osv.osv):
    _name = 'taxpayer.payment'
    _columns = {
        'name': fields.char('Name'),
        'date': fields.datetime('Date'),
        'online_payment_date': fields.datetime('Online Payment Date'),
        'payment_done_date': fields.datetime('Payment Done Date'),
        'bank_transfer_date': fields.datetime('Bank Transfer Date'),
        'bank_payment_confirm_date': fields.datetime('Bank Payment Confirm Date'),
        'user_id': fields.many2one('res.users', 'User'),
        'partner_id': fields.many2one('res.partner', 'Profile'),
        'tin': fields.char('Tin'),
        'state': fields.selection([('new', 'Draft'),
                                   ('online_payment', 'Online Payment'),
                                   ('payment_done', 'Update Payment'),
                                   ('bank_transfer', 'Bank Transfer'),
                                   ('bank_payment_confirm', 'Confirm Payment'),
                                   ('close', 'Close')],
                                  'State', readonly=True),
    }

    def _get_tin(self, cr, uid, context=None):
        val = {}
        partner_ids = self.pool.get('res.partner').search(cr, uid, [('user_id', '=', uid)])
        if partner_ids:
             partner = self.pool.get('res.partner').browse(cr, uid, partner_ids[0]).number
             return partner
        return False

    _defaults = {
        'tin': _get_tin,
        'state': 'new',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def onchange_payment_done_date(self, cr, uid, ids, payment_done_date, context=None):
        val = {}
        if payment_done_date:
            new_payment_done_date = datetime.strptime(payment_done_date, '%Y-%m-%d %H:%M:%S')
            if new_payment_done_date >= datetime.now():
                val['payment_done_date'] = ''
                msg = {'title': 'User Error!', 'message': _('You must select less than today Date.')}
                return {'warning': msg, 'value': val}
        return {'value': val}

    def action_confirm_taxpayer(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'online_payment', 'online_payment_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_payment_done(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'payment_done', 'payment_done_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_bank_transfer(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'bank_transfer', 'bank_transfer_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_bank_pay_confirm(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids,
                         {'state': 'bank_payment_confirm', 'bank_payment_confirm_date': time.strftime('%Y-%m-%d')},
                         context=context)
        return obj

    def action_close_tax(self, cr, uid, ids, context=None):
        obj = self.write(cr, uid, ids, {'state': 'close',}, context=context)
        return obj
