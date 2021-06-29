import time
from openerp.report import report_sxw

class ppt_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(ppt_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>ppt_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.ppt_report','select.tax.form','addons/etax/report/ppt_report.rml',parser=ppt_report)
