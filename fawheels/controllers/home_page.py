from openerp.addons.website.controllers.main import Website
import base64
import json
from psycopg2 import IntegrityError
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp.addons.base.ir.ir_qweb import nl2br



class website_sale(Website):
    @http.route('/page/<page:page>', type='http', auth="public", website=True, cache=300)
    def page(self, page, **opt):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context, request.registry
        values = {
            'path': page,
            'deletable': True, # used to add 'delete this page' in content menu
        }
        # /page/website.XXX --> /page/XXX
        if page.startswith('website.'):
            return request.redirect('/page/' + page[8:], code=301)
        elif '.' not in page:
            page = 'website.%s' % page

        try:
            request.website.get_template(page)
        except ValueError, e:
            # page not found
            if request.website.is_publisher():
                values.pop('deletable')
                page = 'website.page_404'
            else:
                return request.registry['ir.http']._handle_exception(e, 404)
        if page == "website.homepage":
            values['brands']  = pool["sb.brands"].search_read(cr, 1, [],['name'] ,context=context)
            values['size_ids'] = pool["sb.model.size"].search_read(cr, 1, [],['name'] ,context=context)
        return request.render(page, values)

