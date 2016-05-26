# -*- coding: utf-8 -*-
##############################################################################
#
#    Snippetbucket.com
#    Copyright (C) Snippetbuckt.com, Tejas Tank, snippetbucket@gmail.com
#    Edited By : Caret Consulting services,
#    Copyright (C) caretcs.com, caretsoftware@gmail.com
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
{
    'name' : 'Wheels Business',
    'version' : '1.0',
    'depends' : ['base','sale', 'sale_crm', 'website_quote', 'crm_claim','hr', 'purchase', 'document'],
    'author' : 'SnippetBucket.com', 'caretcs.com'
    'category': 'sale',
    'description': """ Wheels Business for refurbishment & sales of vehicle parts.
""",
    'website': 'http://www.caretcs.com',
    'data': [
         'data.xml',
         'security/sb_wheels_security.xml',
         'security/ir.model.access.csv',
         'views/job_order_view.xml',
         'views/sb_wheels_view.xml', 
        'views/account_invoice_view.xml',
         'views/crm_claim_view.xml',
         'views/product_view.xml',
         'views/purchase_view.xml',
         'views/res_company_view.xml',
         'views/res_partner_view.xml',
         'views/sale_order_view.xml',
         'views/stock_view.xml',
         'sequences.xml',
         'views/report_menu.xml',

            ],
    'js': [],
    'demo': ['sequences.xml'],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
