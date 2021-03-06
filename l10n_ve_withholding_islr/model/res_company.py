#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Yanina Aular           <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp.tools import config
import time
import datetime

class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'automatic_income_wh':fields.boolean('Automatic Income Withhold', 
            help='When True, Supplier Income Withholding will be check and '\
                    'validate automatically'),
    }

    defaults = {
        'automatic_income_wh': False,
    }
