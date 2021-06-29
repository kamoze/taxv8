import time
from openerp.report import report_sxw

class cit_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(cit_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>cit_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.cit_report','select.tax.form','addons/etax/report/cit_report.rml',parser=cit_report)