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
    'name': 'Fawheels',
    'version': '9.0.1.0.0',
    'author': 'Caeret Consulting Services',
    'website': 'http://www.caretcs.com',
    'category': 'Website',
    'depends': ['website',
                'website_crm',
                'website_sale',
                'website_quote',
                'website_recaptcha_reloaded',
                'sb_wheels',
                'website_blog',
                ],
    'description': """/

============================

    """,
    'data': [
        'security/ir.model.access.csv',
        'views/fawheels_template.xml',
        'views/product_view.xml',
        'data/fawheels_data.xml',
        'multiple_product_image/views/product_config_view.xml',
        'multiple_product_image/views/product_view.xml', 
        'multiple_product_image/views/product_template.xml',
        'multiple_product_image/security/ir.model.access.csv',
        'views/website_customer_comment.xml',
        'views/website_blog_post_view.xml',
    ],
    'demo': [],
    'installable': True,
}
