# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class DiamondWebPayController(http.Controller):
    _return_url = '/payment/diamondwebpay/return'
    _cancel_url = '/payment/diamondwebpay/cancel'
    _exception_url = '/payment/diamondwebpay/error'
    _reject_url = '/payment/diamondwebpay/reject'

    @http.route([
        '/payment/diamondwebpay/return',
        '/payment/diamondwebpay/cancel',
        '/payment/diamondwebpay/error',
        '/payment/diamondwebpay/reject',
    ], type='http', auth='none')
    def diamondwebpay_return(self, **post):
        """ diamondwebpay."""
        _logger.info('diamondwebpay: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'diamondwebpay', context=request.context)
        return_url = post.pop('return_url', '')
        if not return_url:
            data ='' + post.pop('ADD_RETURNDATA', '{}').replace("'", "\"")
            custom = json.loads(data)
            return_url = custom.pop('return_url', '/')
        return werkzeug.utils.redirect(return_url)
