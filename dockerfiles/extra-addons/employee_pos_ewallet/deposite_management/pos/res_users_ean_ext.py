
import math

from openerp.osv import osv, fields

import  openerp.addons.pos_self_service.point_of_sale.product


class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'ean13' : fields.char('EAN13', size=13, help="BarCode"),
        'pos_config' : fields.many2one('pos.config', 'Default Point of Sale', domain=[('state', '=', 'active')]),
    }

    def _check_ean(self, cr, uid, ids, context=None):
        return all(
            openerp.addons.pos_self_service.point_of_sale.product.check_ean(user.ean13) == True
            for user in self.browse(cr, uid, ids, context=context)
        )

    _constraints = [
        (_check_ean, "Error: Invalid ean code", ['ean13'],),
    ]

