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


from openerp.osv import osv, fields
import time
from openerp.tools import config
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp


class account_wh_src(osv.osv):

    def name_get(self, cursor, user, ids, context=None):
        """ To generate a name for src record
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        res = []
        data_move = self.pool.get('account.wh.src').browse(cursor, user, ids, context=context)
        for move in data_move:
            if not move.name:
                if move.number:
                    name = move.number
                else:
                    name = 'CRS * ID = ' + str(move.id)
            else:
                name = move.name
            res.append((move.id, name))
        return res

    def _get_uid_wh_agent(self, cr, uid, context=None):
        """ Return true if current partner is social responsability agent and
        return false in otherwise
        """
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        ru_obj = self.pool.get('res.users')
        ru_brw = ru_obj.browse(cr, uid, uid, context = context)
        acc_part_brw = rp_obj._find_accounting_partner(ru_brw.company_id.partner_id)
        return acc_part_brw.wh_src_agent

    def _get_partner_agent(self, cr, uid, context=None):
        """ Return a list of browse partner depending of invoice type
        """
        obj_partner = self.pool.get('res.partner')
        args = [('parent_id','=',False)]
        context = context or {}
        res = []
        
        if context.get('type') in ('out_invoice',):
            args.append(('wh_src_agent','=',True))
        partner_ids = obj_partner.search(cr, uid, args)
        if partner_ids:
            partner_brw = obj_partner.browse(cr, uid, partner_ids, context=context)
            res = map(lambda x: x.id, partner_brw)
        return res

    def default_get(self, cr, uid, fields, context=None):
        """ Update fields uid_wh_agent and partner_list to the create a
        record        
        """
        context = context or {}
        res = super(account_wh_src, self).default_get(cr, uid, fields, context=context)
        res.update({'uid_wh_agent': self._get_uid_wh_agent(cr,uid,context=context) })
        res.update({'partner_list': self._get_partner_agent(cr,uid,context=context) })
        
        return res

    def _get_p_agent(self, cr, uid, ids, field_name, args, context=None):
        """ Create a dictionary with ids partner and their browse item 
        """
        context = context or {}
        res= {}.fromkeys(ids,self._get_partner_agent(cr,uid,context=context))
        return res 

    def _get_wh_agent(self, cr, uid, ids, field_name, args, context=None):
        """ Create a dictionary with ids agent partner and their browse item
        """
        context = context or {}
        res= {}.fromkeys(ids,self._get_uid_wh_agent(cr,uid,context=context))
        return res 

    _name = "account.wh.src"
    _description = "Social Responsibility Commitment Withholding"
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly',False)]}, help="Description of withholding"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Withholding reference"),
        'number': fields.char('Number', size=32, states={'draft':[('readonly',False)]}, help="Withholding number"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ],'Type', readonly=False, help="Withholding type"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', readonly=True, help="Status Voucher"),
        'date_ret': fields.date('Withholding date', readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the current date"),
        'date': fields.date('Date', readonly=True, states={'draft':[('readonly',False)]}, help="Date"),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','!=','done')], readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the period of the validation(Withholding date) date."),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The pay account used for this withholding."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Withholding customer/supplier"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal entry"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'line_ids': fields.one2many('account.wh.src.line', 'wh_id', 'Local withholding lines', readonly=True, states={'draft':[('readonly',False)]}, help="Invoices which deductions will be made"),
        'wh_amount': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withheld"),
        
        'uid_wh_agent': fields.function(_get_wh_agent, type='boolean', string="uid_wh_agent", store=False, help='indicates whether the current user is agent'),
        'partner_list' : fields.function(_get_p_agent, type='char', string='Lista', store=False, method=False, help='partners are only allowed to be withholding agents'),

    } 
    
    def _diario(self, cr, uid, model, context=None):
        """  Return journal to use in purchase or sale
        """
        if context is None:
            context={}
        ir_model_data = self.pool.get('account.journal')
        journal_purchase = ir_model_data.search(cr, uid, [('type','=','src_purchase')])
        journal_sale = ir_model_data.search(cr, uid, [('type','=','src_sale')])
        ir_model_purchase_brw = ir_model_data.browse(cr, uid, journal_purchase, context=context)
        ir_model_sale_brw=ir_model_data.browse(cr, uid, journal_sale, context=context)
        if context.get('type') == 'in_invoice':
            return ir_model_purchase_brw[0].id
        else:
            return ir_model_sale_brw[0].id


    _defaults = {
    'state': lambda *a: 'draft',
    'currency_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,
    'journal_id': _diario,
    'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    _sql_constraints = [
    ] 
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,context=None):
        """ Return account depending of the invoice         
        @param type: invoice type
        @param partner_id: partner id
        """
        if context is None: context = {}    
        acc_part_brw = False
        acc_id = False
        res = {}
        inv_obj = self.pool.get('account.invoice')
        rp_obj = self.pool.get('res.partner')
        wh_line_obj = self.pool.get('account.wh.src.line')
        
        if partner_id:
            acc_part_brw = rp_obj._find_accounting_partner(rp_obj.browse(cr, uid, partner_id))
            if type in ('out_invoice', 'out_refund'):
                acc_id = acc_part_brw.property_account_receivable and acc_part_brw.property_account_receivable.id or False
            else:
                acc_id = acc_part_brw.property_account_payable and acc_part_brw.property_account_payable.id or False

        part_brw = ids and rp_obj._find_accounting_partner(self.browse(cr, uid, ids[0], context=context).partner_id)
        wh_lines = ids and wh_line_obj.search(cr, uid, [('wh_id', '=', ids[0])])
        if not partner_id: 
            wh_lines and wh_line_obj.unlink(cr, uid, wh_lines)
            wh_lines = []
        if part_brw and acc_part_brw and part_brw.id != acc_part_brw.id:
            wh_lines and wh_line_obj.unlink(cr, uid, wh_lines)
            wh_lines = []
        
        return {'value': {
                    'line_ids':wh_lines,
                    'account_id': acc_id,
                }
        }
        

    def action_date_ret(self,cr,uid,ids,context=None):
        """ if the retention date is empty, is filled with the current date
        """
        for wh in self.browse(cr, uid, ids, context):
            wh.date_ret or self.write(cr, uid, [wh.id], {'date_ret':time.strftime('%Y-%m-%d')})
        return True


    def action_draft(self, cr, uid, ids, context={}):
        """ Passes the document to draft status
        """
        if context is None:
            context={}
        inv_obj = self.pool.get('account.invoice')
        
        brw = self.browse(cr,uid,ids[0],context)
        inv_ids = [i.invoice_id.id for i in brw.line_ids]
        if inv_ids:
            inv_obj.write(cr,uid,inv_ids,{'wh_src_id':False})
                
        return self.write(cr,uid,ids[0],{'state':'draft'})

    def action_confirm(self, cr, uid, ids, context={}):
        """ Retention is valid to pass a status confirmed
        """
        if context is None:
            context={}
        inv_obj = self.pool.get('account.invoice')
        
        brw = self.browse(cr,uid,ids[0],context)
        line_ids = brw.line_ids
        if not line_ids:
            raise osv.except_osv(_('Invalid Procedure!'),_("No retention lines"))
        
        res = [True]
        res+=[False for i in line_ids if i.wh_amount <= 0.0 or i.base_amount  <= 0.0 or i.wh_src_rate  <= 0.0 ]
        if not all(res):
            raise osv.except_osv(_('Invalid Procedure!'),_("Verify retention lines not have Null values(0.00)"))
        
        res = 0.0
        for i in line_ids:
            res+=i.wh_amount
        if abs(res - brw.wh_amount) > 0.0001:
            raise osv.except_osv(_('Invalid Procedure!'),_("Check the amount of withholdings"))
        
        inv_ids = [i.invoice_id.id for i in brw.line_ids]
        if inv_ids:
            inv_obj.write(cr,uid,inv_ids,{'wh_src_id':ids[0]})
        
        return self.write(cr,uid,ids[0],{'state':'confirmed'})
        
    def action_done(self, cr, uid, ids, context=None):
        """ Pass the document to state done
        """
        if context is None:
            context = {}

        self.action_date_ret(cr, uid, ids, context=context)
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids, context=context)
        
        return self.write(cr,uid,ids,{'state':'done'})
        
    def _dummy_cancel_check(self, cr, uid, ids, context=None):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True

    def cancel_check(self, cr, uid, ids, context=None):
        '''
        Unique method to check if we can cancel the Withholding Document
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        if not self._dummy_cancel_check(cr, uid, ids, context=context):
            return False
        return True

    def cancel_move(self,cr,uid,ids, *args):
        """ Delete move lines related with withholding vat and cancel
        """
        ids = isinstance(ids, (int, long)) and [ids] or ids
        am_obj = self.pool.get('account.move')
        for ret in self.browse(cr, uid, ids):
            if ret.state == 'done':
                for ret_line in ret.line_ids:
                    ret_line.move_id and am_obj.button_cancel(cr, uid, [ret_line.move_id.id])
                    ret_line.move_id and am_obj.unlink(cr, uid,[ret_line.move_id.id])
            ret.write({'state':'cancel'})
        return True    

    def clear_wh_lines(self, cr, uid, ids, context=None):
        """ Clear lines of current withholding document and delete wh document
        information from the invoice.
        """
        context = context or {}
        awsl_obj = self.pool.get('account.wh.src.line')
        ai_obj = self.pool.get('account.invoice')
        if ids:
            awsl_ids = awsl_obj.search(cr, uid, [('wh_id', 'in', ids)],
                    context=context)
            ai_ids = awsl_ids and [ awsl.invoice_id.id
                for awsl in awsl_obj.browse(cr, uid, awsl_ids, context=context) ]
            ai_ids and ai_obj.write(cr, uid, ai_ids,
                                    {'wh_src_id': False}, context=context)
            awsl_ids and awsl_obj.unlink(cr, uid, awsl_ids, context=context)

        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Call cancel_move and return True
        """
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        self.cancel_move(cr, uid, ids)
        self.clear_wh_lines(cr, uid, ids, context=context)
        return True

    def copy(self,cr,uid,id,default,context=None):
        """ Lines can not be duplicated in this model
        """
        raise osv.except_osv('Invalid Procedure!',"You can not duplicate lines")
        return True

    def unlink(self, cr, uid, ids, context=None):
        """ Overwrite the unlink method to throw an exception if the
        withholding is not in cancel state."""
        context = context or {}
        for src_brw in self.browse(cr, uid, ids, context=context):
            if src_brw.state != 'cancel':
                raise osv.except_osv(_("Invalid Procedure!!"),
                    _("The withholding document needs to be in cancel state to be deleted."))
            else:
                super(account_wh_src, self).unlink(cr, uid, ids, context=context)
        return True

    def action_move_create(self, cr, uid, ids, context=None):
        """ Build account moves related to withholding invoice 
        """
        inv_obj = self.pool.get('account.invoice')
        if context is None: context = {}
        
        context.update({'wh_src':True})
        
        ret = self.browse(cr, uid, ids[0], context)

        for line in ret.line_ids:
            if line.move_id:
                raise osv.except_osv(_('Invoice already withhold !'),\
                _("You must omit the follow invoice '%s' !") %\
                (line.invoice_id.number,))

        acc_id = ret.account_id.id

        period_id = ret.period_id and ret.period_id.id or False
        journal_id = ret.journal_id.id
        if not period_id:
            per_obj = self.pool.get('account.period')
            period_id = per_obj.find(cr, uid,ret.date_ret or time.strftime('%Y-%m-%d'))
            #Due to the fact that demo data for periods sets 'special' as True on them, this little
            #hack is necesary if this issue is solved we should ask directly for the 
            #refer to this bug for more information 
            #https://bugs.launchpad.net/openobject-addons/+bug/924200
            demo_enabled = self.pool.get('ir.module.module').search(cr, uid,
                                                            [('name', '=', 'base'),
                                                             ('demo', '=', True)])
            args = [('id','in',period_id)]
            if not demo_enabled:
                args.append(('special','=',False))
            period_id = per_obj.search(cr,uid,args)
            if not period_id:
                raise osv.except_osv(_('Missing Periods!'),\
                _("There are not Periods created for the pointed day: %s!") %\
                (ret.date_ret or time.strftime('%Y-%m-%d')))
            period_id = period_id[0]
        if period_id:
            if ret.line_ids:
                for line in ret.line_ids:
                    writeoff_account_id,writeoff_journal_id = False, False
                    amount = line.wh_amount
                    if line.invoice_id.type in ['in_invoice','in_refund']:
                        name = 'COMP. RET. CRS ' + ret.number + ' Doc. '+ (line.invoice_id.supplier_invoice_number or '')
                    else:
                        name = 'COMP. RET. CRS ' + ret.number + ' Doc. '+ (line.invoice_id.number or '')
                    ret_move = inv_obj.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, ret.date_ret, name,[line], context)
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'line_ids':lines, 'period_id':period_id})

                    if rl and line.invoice_id.type in ['out_invoice','out_refund']:
                        inv_obj.write(cr,uid,[line.invoice_id.id],{'wh_src_id':ret.id})
            else:
                return False
        return True

    def action_number(self, cr, uid, ids, *args):
        """ Is responsible for generating a number for the document if it does not have one  
        """
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_wh_src ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')


            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.src.%s' % obj_ret.type)
                cr.execute('UPDATE account_wh_src SET number=%s ' \
                        'WHERE id=%s', (number, id))

                
        return True
        
        
    def wh_src_confirmed(self, cr, uid, ids):
        """ Confirm src document
        """
        number = self.pool.get('account.wh.src.line')
        return True
        

        

class account_wh_src_line(osv.osv):

    _name = "account.wh.src.line"
    _description = "Social Responsibility Commitment Withholding Line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Local Withholding line Description"),
        'wh_id': fields.many2one('account.wh.src', 'Local withholding', ondelete='cascade', help="Local withholding"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='set null', help="Withholding invoice"),
        'base_amount':fields.float('Base Amount', digits_compute= dp.get_precision('Base Amount to be Withheld'), help='amount to be withheld'),
        'wh_amount':fields.float('Withheld Amount', digits_compute= dp.get_precision('Withhold'), help='withheld amount'),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account Entry"),
        'wh_src_rate':fields.float('Withholding Rate', help="Withholding rate"),
    }
    _defaults = {

    }
    _sql_constraints = [

    ] 
    
    def onchange_invoice_id(self, cr, uid, ids, type, invoice_id=False,base_amount=0.0,wh_src_rate=5.0,context=None):
        """ Change src information to change the invoice 
        @param type: invoice type
        @param invoice_id: new invoice id
        @param base_amount: new base amount
        @param wh_src_rate: new rate of the withhold src
        """
        if context is None: context = {}    
        res = {}
        inv_obj = self.pool.get('account.invoice')
        if not invoice_id:
            return {'value': {
                        'invoice_id': False,
                        'base_amount': 0.0,
                        'wh_src_rate': 0.0,
                        'wh_amount': 0.0,}
                    }
        
        inv_brw = inv_obj.browse(cr, uid, invoice_id)
        base_amount = base_amount or inv_brw.amount_untaxed
        wh_src_rate = wh_src_rate or inv_brw.wh_src_rate or 5.0
        wh_amount = base_amount * wh_src_rate/100.0
        res = {'value': {
            'base_amount': base_amount,
            'wh_src_rate': wh_src_rate,
            'wh_amount': wh_amount,
            }
        }
        return res
