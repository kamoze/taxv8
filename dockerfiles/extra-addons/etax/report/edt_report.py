import time
from openerp.report import report_sxw

class edt_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(edt_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>ppt_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.edt_report','select.tax.form','addons/etax/report/edt_report.rml',parser=edt_report)