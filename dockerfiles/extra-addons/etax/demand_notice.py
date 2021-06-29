from openerp.osv import fields,osv
from openerp.tools.translate import _
from datetime import date, datetime, timedelta
import time
import urllib2
import urllib

class etax_demand_notice(osv.osv):
    _name='etax.demand.notice'
    
    _columns={
        'partner_id' : fields.many2one('res.partner','Tax Payer',required=True),
        'comment' : fields.text('Message'),
    }
    
    def print_demand_notice(self,cr,uid,ids,context=None):
        datas = {
                  'model': 'etax.demand.notice',
                  'ids': ids,
                }
        return {'type': 'ir.actions.report.xml', 'report_name':'demand_notice_report','datas': datas,'nodestroy':True}


    def send_demand_notice(self,cr,uid,ids,context=None):
	for val in self.browse(cr, uid,ids):
		url='http://api.infobip.com/api/v3/sendsms/plain?user=spanbox&password=cyini74&sender=DELTA_TAX&SMSText='+str(urllib2.quote(val.comment))+'&GSM='+str(val.partner_id.mobile)
		response = urllib2.urlopen(url)
		print'json_response===',response,url
#        datas = {
#                  'model': 'etax.demand.notice',
#                  'ids': ids,
#                }
        return True
