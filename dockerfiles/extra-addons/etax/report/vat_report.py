import time
from openerp.report import report_sxw

class vat_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(vat_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>vat_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.vat_report','select.tax.form','addons/etax/report/vat_report.rml',parser=vat_report)