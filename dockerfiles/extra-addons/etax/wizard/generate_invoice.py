from openerp.osv import osv, fields
class generate_invoice(osv.osv_memory):
    _name='generate.invoice'
    _columns={
              #'taxpayer':fields.selection([('self_employed','Self Employed'),('corporate','Corporate'),('employed','Employed')],'Taxpayer Profile'),
              'relevant_tax':fields.float('Relevant Tax'),
              'assessment_charges':fields.float('Assessment Charges'),
              'other_admin_charges':fields.float('Other Admin Charges'),
              'assessment_id':fields.many2one('tax.calculator.individual','Assessment Id')
              
              }
    def create_invoice(self, cr, uid, ids, context=None):
        res={}
        inv_obj=self.pool.get('account.invoice')
        inv_line_obj=self.pool.get('account.invoice.line')
        journal_id=self.pool.get('account.journal').search(cr, uid, [('type','=','sale')])
        print"-----",journal_id
        for val in self.browse(cr, uid, ids):
            if val.relevant_tax>0:
                create_id=inv_obj.create(cr,uid,{'partner_id':val.assessment_id.name.id,'account_id':val.assessment_id.name.property_account_receivable.id,'jornal_id':journal_id[0],
                'currency_id':self.pool.get('res.users').browse(cr,uid,uid).company_id.currency_id.id })
                print"create_id======",create_id

                product_id=self.pool.get('product.product').search(cr,uid,[('type','=','service')])
                print "product_id============",product_id
                prepare_invoice_line={'product_id':product_id[0],'name':self.pool.get('product.product').browse(cr,uid,product_id[0]).name,'invoice_id':create_id,'quantity':1,'price_unit':val.relevant_tax}
                create_invoice_line_id=inv_line_obj.create(cr,uid,prepare_invoice_line,context=context)

                if val.other_admin_charges>0.0:
                    prepare_invoice_line={'product_id':val.assessment_id.name.tax_config_id.admin_charges_product.id,'name':val.assessment_id.name.tax_config_id.admin_charges_product.name,'invoice_id':create_id,'quantity':1,'price_unit':val.other_admin_charges}
                    create_invoice_line_id=inv_line_obj.create(cr,uid,prepare_invoice_line,context=context)
                if val.assessment_charges>0.0:
                    prepare_invoice_line={'product_id':val.assessment_id.name.tax_config_id.assessment_charges_product.id,'name':val.assessment_id.name.tax_config_id.assessment_charges_product.name,'invoice_id':create_id,'quantity':1,'price_unit':val.assessment_charges}
                    create_invoice_line_id=inv_line_obj.create(cr,uid,prepare_invoice_line,context=context)

                print "create_invoice_line_id===========",create_invoice_line_id
             
                res=self.write(cr,uid,ids,{'state':'invoice','invoice_id':create_id},context=context)
                print"ressss======================",res
        return res
    
    def default_get(self,cr,uid,fields,context=None):
        print "fields=======",fields
        print"context=======",context
        res={}
        if context is None:
            context={}
        assesment=context.get('active_id',False)
        relevant_tax_id=context.get('active_id',False)
        print "relevant_tax_id===============",assesment
        if 'assessment_id' in fields:
            res.update({'assessment_id':assesment})
        if 'relevant_tax' in fields:
            res.update({'relevant_tax':self.pool.get('tax.calculator.individual').browse(cr,uid, assesment).tax_liability})
        if 'other_admin_charges' in fields:
            res.update({'other_admin_charges':self.pool.get('tax.calculator.individual').browse(cr,uid, assesment).admin_charges})
        if 'assessment_charges' in fields:
            res.update({'assessment_charges':self.pool.get('tax.calculator.individual').browse(cr,uid, assesment).assessment_charges})
        print "res======",res
        return res
    
    
    
    