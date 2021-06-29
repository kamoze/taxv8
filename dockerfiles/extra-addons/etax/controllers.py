import openerp
from openerp.addons.web.controllers.main import WebClient
from openerp.addons.web import http
from openerp.http import request, STATIC_CACHE
from openerp.tools import image_save_for_web

class NewPage(http.Controller):
        @http.route('/page/assesment/',auth='public', website=True)
        def assesment(self,**kw):
            return http.request.render('etax.assesment')

        @http.route('/info/enablers', type='http', auth="public", website=True, methods=['POST'])
        def create_info(self, **post):

            etax_id = request.env['tax.calculator.individual'].sudo().create(
                {'name': request.session.uid,
                 'trading_profit':post['trading_profile'],
                 'buisness_income': post['business_income'],
                 'other_profits': post['other_profit'],
                 'professional_income': post['professional_income'],
                 'salary': post['salary'],
                 'commission': post['commision'],
                 'bonuses': post['bonus'],
                 'gratuties': post['gratuties'],
                 'fees': post['fees'],
                 'benefits_in_kind': post['benifit_in_kind'],
                 'other_income': post['other_income'],

                 'dividends': post['dividiends'],
                 'interest': post['interest'],
                 'rent': post['rent_gross'],
                 'royalities': post['royalities'],
                 'others': post['other_gross'],

                 'gratuities': post['gratuities_sd'],
                 'pensions_contributions': post['pensions_contributions'],
                 'nhf_contributions': post['nhf_contributions'],
                 'ins_superannuations': post['ins_superannuations'],
                 'nhis_contributions': post['nhis_contributions'],
                 'mortgage_interest': post['mortgage_interest'],
                 'subuscription': post['professional_body'],
                 'life_assurance_relif': post['life_relief'],
                 'capital_allowances': post['capital_allowances'],
                 'balancing_charges': post['balancing_charges'],
                 'balancing_allowaces': post['balancing_allowaces'],
                 'losses': post['losses'],
                 })

            return request.render('etax.create_etax_record')