import time
from openerp.report import report_sxw

class cgt_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(cgt_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>cgt_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.cgt_report','select.tax.form','addons/etax/report/cgt_report.rml',parser=cgt_report)