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
    'name': 'SO_INV_Global_Discount',
    'version': '1.0',
    'category': 'extra',
        'sequence': 1,
    'summary': "Show Discount Total and Total before Discount on Sale Order, Invoice. ",
    'description':"Show Discount Total and Total before Discount on Sale Order, Invoice.",
    'author': 'Caret Consulting Services',
    'website': 'www.caretcs.com',
    'depends': ['sale', 'account_voucher', 'sb_wheels'],
    'data': [
        'views/invoice_discount_view.xml',
        'views/sale_discount_view.xml',
        #'views/report_invoice_discount.xml',
        #'views/report_sale_discount.xml',
    ],
    'installable': True,
    'auto_install': False,
}


