import time
from openerp.report import report_sxw

class pit_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(pit_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>pit_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.pit_report','select.tax.form','addons/etax/report/pit_report.rml',parser=pit_report)