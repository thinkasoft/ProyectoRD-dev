#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>     
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
################################################################################

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {        
        'wh_src_collected_account_id': fields.many2one(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Collected Withholding SRC Account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used when applying a withhold to an Supplier"),
        'wh_src_paid_account_id': fields.many2one(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Paid Withholding SRC Account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used when applying a withhold to a Customer"),
    }