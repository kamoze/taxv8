
import math

from openerp.osv import osv, fields

import openerp.addons.pos_self_service.point_of_sale.product


class res_users(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'ean13' : fields.char('EAN13', size=13, help="BarCode"),
    }

    def _check_ean(self, cr, uid, ids, context=None):
        """ TO Invalid res_partner for EAN Number """
        return 1


    _constraints = [
        (_check_ean, "Error: Invalid ean code 1", ['ean13'],),
    ]

