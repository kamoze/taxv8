import time
from openerp.report import report_sxw

class nitdf_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(nitdf_report,self).__init__(cr,uid,name,context)
        self.localcontext.update({'time':time,})
        print">>>>>>>>>>nitdf_report>>>>>>>>>>>>>>>"
        
report_sxw.report_sxw('report.nitdf_report','select.tax.form','addons/etax/report/nitdf_report.rml',parser=nitdf_report)