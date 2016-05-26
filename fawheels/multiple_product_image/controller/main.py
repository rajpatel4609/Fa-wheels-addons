# -*- coding: utf-8 -*-
import werkzeug
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.tools.translate import _
from openerp.osv import orm

class product_zoom_config(website_sale):
        
    @http.route(['/product/zoom_type'], type='json', auth="public", website=True)
    def get_zoom_type(self, type_id=None):
        cr, uid, context = request.cr, request.uid, request.context
        result=False
        result=request.website.inner_zoom
        return result  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
