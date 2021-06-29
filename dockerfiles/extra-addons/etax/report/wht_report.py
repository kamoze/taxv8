import time
from openerp.report import report_sxw

class wht_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(wht_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>wht_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.wht_report','select.tax.form','addons/etax/report/wht_report.rml',parser=wht_report)