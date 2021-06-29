# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-TODAY Acespritech Solutions Pvt Ltd
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#   
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api,_
import urllib
import urllib2
from openerp.exceptions import except_orm, Warning, RedirectWarning
from lxml import etree
from openerp.osv.orm import setup_modifiers

import logging
_logger = logging.getLogger(__name__)


class sms_config(models.Model):
    _name = 'sms.config'

    url = fields.Char('URL', size=64,
                      default='http://api.infobip.com/api/v3/sendsms/plain', required=True)
    login = fields.Char('Login', size=64, required=True)
    password = fields.Char('Password', size=64, required=True)
    sender = fields.Char('Sender', size=64, required=True)
    active = fields.Boolean('Active', default=True)

    @api.model
    def send_sms(self, phone, message):
        """
        Send SMS for every sales from POS
        :param phone:
        :param message:
        :return:
        """
        sms_id = self.search([('active', '=', True)])
        if sms_id:
            url = str(sms_id.url).strip()
            login = str(sms_id.login).strip()
            password = str(sms_id.password).strip()
            sender = str(sms_id.sender).strip()
            params = urllib.urlencode({
                'user': login,
                'password': password,
                'sender': sender,
                'GSM': phone,
                'SMSText': message,
             })
            try:
                request = urllib2.Request(url, params)
                response = urllib2.urlopen(request)
                result = response.read()
            except Exception, e:
                _logger.error(_('Unable to send SMS on %s' % phone))
                pass
        return True

sms_config()

