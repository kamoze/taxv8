# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import fields, models, api,_
from datetime import date,datetime
from collections import defaultdict, OrderedDict


class shop_report(models.AbstractModel):
    _name = 'report.employee_pos_ewallet.template_shop_report'


    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('employee_pos_ewallet.template_shop_report')
        docargs = {
           'doc_ids': self.env['shop.report.wizard'].browse(data['ids']),
           'doc_model': report.model,
           'docs': self,
           'summary_shop': self.summary_shop,
       }
        return report_obj.render('employee_pos_ewallet.template_shop_report', docargs)

    def summary_shop(self,obj):
        if not obj.payment_method_ids:
           journal_ids = [journal.id for journal in self.env['account.journal'].search([])]
        else:
            journal_ids = [journal.id for journal in obj.payment_method_ids]
            
        if not obj.location_ids:
           loc_ids = [loc.id for loc in self.env['stock.location'].search([])]
        else:
            loc_ids = [loc.id for loc in obj.location_ids]
        if obj.state and not obj.interface:
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s' AND state = '%s'
                    AND location_id IN %s AND sale_journal IN %s
                    ORDER BY name"""% (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59', obj.state
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        if not obj.state and not obj.interface:
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s'
                    AND location_id IN %s AND sale_journal IN %s
                    ORDER BY name"""% (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59'
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        if not obj.state and obj.interface == 'self_service':
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s'
                    AND location_id IN %s AND sale_journal IN %s AND is_self_service IS TRUE
                    ORDER BY name"""% (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59'
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        if not obj.state and obj.interface == 'normal':
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s'
                    AND location_id IN %s AND sale_journal IN %s AND is_self_service IS False
                    ORDER BY name"""% (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59'
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        if not obj.interface and not obj.state:
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s'
                    AND location_id IN %s AND sale_journal IN %s
                    ORDER BY name"""% (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59'
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        if obj.interface == 'self_service':
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s' AND state = '%s'
                    AND location_id IN %s AND sale_journal IN %s AND is_self_service IS TRUE
                    ORDER BY name"""% (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59', obj.state
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        if obj.interface == 'normal':
            query = """SELECT name, date_order, session_id, id, location_id, state 
                    from pos_order
                    WHERE date_order >= '%s'
                    AND date_order <= '%s' AND state = '%s'
                    AND location_id IN %s AND sale_journal IN %s AND is_self_service IS FALSE
                    ORDER BY name""" % (obj.date_start+' '+'00:00:00', obj.date_end+' '+'23:59:59', obj.state
                            , " (%s) " % ','.join(map(str, loc_ids))
                            ," (%s) " % ','.join(map(str, journal_ids)))
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        location_dict = defaultdict(list)
        
        for each in results:
            amount_total = self.env['pos.order'].sudo().browse(each['id']).amount_total
            location_id = self.env['stock.location'].browse(each['location_id'])
            session_id = self.env['pos.session'].browse(each['session_id'])
            each.update({'amount': amount_total or 0,
                         'location_name': location_id.complete_name,
                         'session_name': session_id.name})
            location_dict[each['location_name']].append(each)
        return dict(location_dict)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: