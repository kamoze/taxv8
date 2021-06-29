# -*- coding: utf-8 -*-
import simplejson

from openerp import http
from openerp.http import request
from openerp.tools.translate import _
import ast


class DataSet(http.Controller):
    
    @http.route('/web/dataset/get_products_qty', type='http', auth="user")
    def get_products_qty(self, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        records = []
        model = kw.get('model')
        pricelist = int(kw.get('pricelist'))
        shop_id = int(kw.get('shop_id'))
        category_ids = kw.get('category_ids')
        product_write_date = kw.get('product_write_date')
        ctx = {'pricelist': pricelist, 'location': shop_id, 'display_default_code': False}
        fields = ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 
                     'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                     'product_tmpl_id','qty_available','type','write_date']
        Model = request.session.model(kw.get('model'))
        if len(category_ids) > 0:
            categ_lst = list(map(int, ast.literal_eval(category_ids)))
            domain = [['sale_ok','=',True],['available_in_pos','=',True], ['pos_categ_id', 'child_of', categ_lst], ['write_date','>',product_write_date]]
        else:
            domain = [['sale_ok','=',True],['available_in_pos','=',True], ['write_date','>',product_write_date]]
        context.update(ctx)
        try:
            records = Model.search_read(domain, fields, 0, False, False, context)
        except Exception, e:
            pass
        return simplejson.dumps(records)