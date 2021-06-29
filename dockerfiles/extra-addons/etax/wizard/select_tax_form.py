from openerp.osv import osv, fields
from openerp.tools.translate import _


class select_tax_form(osv.osv_memory):
    _name='select.tax.form'
    _inherit = ['mail.thread']
#    _rec_name='tax_form'
    _columns={
        'tax_form' : fields.selection([('Company Income Tax (CIT)','Company Income Tax (CIT)'),
                                       ('Petroleum Proit Tax (PPT)','Petroleum Proit Tax (PPT)'),
                                       ('Value Added Tax (VAT)','Value Added Tax (VAT)'),
                                       ('Personal Income Tax (PIT)','Personal Income Tax (PIT)'),
                                       ('Witholding Tax (WHT)','Withholding Tax (WHT)'),
                                       ('Capital Gains Tax (CGT)','Capital Gain Tax (CGT)'),
                                       ('National Information Tech Dev Fund Levy (NITDF)','National Information Tech Dev Fund Levy (NITDF)'),
                                       ('Education Tax (EDT)','Education Tax (EDT)')],'Select Tax Form'),
        'tax_payer_id' : fields.many2one('res.partner','Name of the Tax payer', domain="[('e_tax','=',True)]",required=True),

        'attachment': fields.many2one('etax.attachment', 'Attachment')
    }
    

    def print_report(self,cr,uid,ids,context=None):
        wiz_obj = self.browse(cr,uid,ids)[0]

        data = wiz_obj.attachment.attachments_id
        name = wiz_obj.attachment.datas
        ctx = dict(context)
        ctx.update({
            'default_attachments_id': data,
            'default_datas': name
        })
        return {
            'name': _('Download'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'file.download',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
    def send_mail_tax_payer(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        email_template_obj = self.pool.get('email.template')
        wiz_obj = self.browse(cr, uid, ids)[0]
        template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=', 'select.tax.form')], context=context)
        attachment_ids = []

        if template_ids and wiz_obj.attachment:
            data = wiz_obj.attachment.attachments_id
            name = wiz_obj.attachment.datas
            att_obj = self.pool.get('ir.attachment')
            attachment_data = {
                'name': name,
                'datas_fname': name,  # your object File Name
                'type': 'binary',
                'res_model': 'select.tax.form',
                'db_datas': data
            }
            attachment_ids.append(att_obj.create(cr, uid, attachment_data, context=context))

        print">>>>>>>>>>>>>>>>>TemplateID>>>>>>>>>>>>>>>>", template_ids
        #         try:
        #             template_id = ir_model_data.get_object_reference(cr, uid, 'isa_crm_helpdesk', 'email_template_edi_purchase')[1]
        #         except ValueError:
        #             template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[
                1]
            print">>>>>>>>>>>>>>>>Compose Form ID>>>>>>>>>>>>>>>", compose_form_id
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'select.tax.form',
            'default_res_id': ids[0],
            'default_use_template': bool(template_ids),
            'default_template_id': template_ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_attachment_ids': [(6, 0, attachment_ids)]
        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }



class filedownload(osv.osv_memory):
    _name ='file.download'
    _columns= {


        'attachments_id': fields.binary('Attachment', required=True),
        'datas': fields.char('data')
    }
