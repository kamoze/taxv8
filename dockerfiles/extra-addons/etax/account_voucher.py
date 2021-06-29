from openerp.osv import fields,osv
from openerp.tools.translate import _



class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'

    def proforma_voucher(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)

        obj = self.browse(cr, uid, ids[0])


        user_id = self.pool.get('res.users').browse(cr, uid, uid)
        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        mail_mail = self.pool.get('mail.mail')
        attachment_ids = []
        try:
            template_id = \
            ir_model_data.get_object_reference(cr, uid, 'etax', "invoice_payment_template")[1]
        except ValueError:
            raise osv.except_osv(_('Configuration Missing!'), _("Email Template not found!"))


        report_obj = self.pool.get('report')
        pdf = report_obj.get_pdf(cr, uid, [obj.id], 'application.report_receipt', data=None, context=context)
        att_obj = self.pool.get('ir.attachment')
        attachment_data = {
            'name': "Receipts",
            'datas_fname': 'receipt.pdf',  # your object File Name
            'type': 'binary',
            'res_model': 'account.voucher',
            'db_datas': pdf
        }
        attachment_ids.append(att_obj.create(cr, uid, attachment_data, context=context))
        mail_obj = email_template_pool.generate_email(
            cr, uid, template_id, obj.id)

        mail_obj.update(
                {'email_from': user_id.login ,
                 'email_to': obj.partner_id.email,
                 'body_html': "Hello "+ '' + obj.partner_id.name  + 'You have paid the Invoice of amount Rs ' + str(obj.amount) ,

                 'subject': "Payment For Invoice Number",
                 'attachment_ids':[(6, 0, attachment_ids)]
                 })

        msg_id = mail_mail.create(cr, uid, mail_obj)

        mail_queue = mail_mail.process_email_queue(cr, uid, [msg_id])
        return True



class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    def write(self, cr, uid, ids, vals, context=None):
        res = super(AccountInvoice, self).write(cr, uid, ids, vals, context)
        groups_obj = self.pool.get('res.groups')
        indivisual = self.pool.get('tax.calculator.individual').search(cr, uid, [('invoice_id', 'in', ids)])
        self_emp_grp_id = groups_obj.search(cr, uid, [
            ('name', '=', 'E-Tax User')])
        if vals.get('state', '') == 'paid' and indivisual:
            self.pool.get('tax.calculator.individual').write(cr, uid,indivisual, {'state': 'paid'})
            for vl in self.pool.get('tax.calculator.individual').browse(cr, uid, indivisual):
                groups_obj.write(cr, uid, self_emp_grp_id, {'users': [(4, vl.user_id.id)],})

        return res
