from openerp.osv import osv, fields

class tax_calculator_reassesment(osv.osv_memory):
    _name='tax.calculator.reassesment'
    _columns={
              'description':fields.char('Description'),
              'reassessment_id':fields.many2one('tax.calculator.individual','Reassesment Id'),
              }
    def default_get(self,cr,uid,fields,context=None):
        print "fields=======",fields
        print"context=======",context
        res={}
        if context is None:
            context={}
        re_assessment_id=context.get('active_id',False)
        if 'reassessment_id' in fields:
            res.update({'reassessment_id':re_assessment_id})
        return res