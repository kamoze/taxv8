import time
from openerp.report import report_sxw

class demand_notice_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(demand_notice_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>demand_notice_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.demand_notice_report','etax.demand.notice','addons/etax/report/demand_notice_report.rml',parser=demand_notice_report)