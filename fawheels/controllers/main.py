# -*- coding: utf-8 -*-
import base64

import json
from psycopg2 import IntegrityError
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp.addons.base.ir.ir_qweb import nl2br
from openerp.addons.website_sale.controllers.main import website_sale, QueryURL,table_compute,get_pricelist, PPG
import openerp.addons.website_sale.controllers.main
openerp.addons.website_sale.controllers.main.PPR = 3

PPR = 3

class website_sale(website_sale):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context, request.registry
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)
        url = "/shop"
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        product_obj = pool.get('product.template')

        attrib_domain = []
        left_search_attrib = {
            'attrib_products': [],
            'attrib_wheels': [],
            'attrib_model': []
        }
        main_search_attrib = {
            'brand_id': "",
            'model_id' : "",
            'size_id': ""
        }
        main_search_value = {
            'brand_id': pool["sb.brands"].search_read(cr, uid, [],['name'] ,context=context),
            'model_id': "",
           'size_id':  pool["sb.model.size"].search_read(cr, uid, [],['name'] ,context=context),
        }

        if post.get("attrib_products"):
            wheel_att = post.get("attrib_products").split("-")
            left_search_attrib['attrib_products'] = wheel_att
            attrib_domain += [('sb_type', 'in', wheel_att)]

        if post.get("attrib_wheels"):
            attrib_wheels = post.get("attrib_wheels").split("-")
            attrib_wheels = [int(x) for x in attrib_wheels]
            left_search_attrib['attrib_wheels'] = attrib_wheels
            attrib_domain += [('size_id', 'in', attrib_wheels)]

        if post.get("attrib_model"):
            attrib_model = post.get("attrib_model").split("-")
            attrib_model = [int(x) for x in attrib_model]
            left_search_attrib['attrib_model'] = attrib_model
            attrib_domain += [('model_id', 'in', attrib_model)]

        if post.get('domain_search'):
            make_id, model_id, size_id = post.get('domain_search').split("-")
            attrib_domain += [ ('make_id', '=', int(make_id)), 
                        ('model_id', '=', int(model_id)), 
                        ('size_id', '=', int(size_id))
                        ]
            main_search_value['model_id'] = pool['sb.vehicle.model'].search_read(cr, uid, [('brand_id', '=', int(make_id))], ['name'])
            main_search_attrib = {
                'brand_id': int(make_id),
                'model_id' : int(model_id),
                'size_id': int(size_id)
             }

        if attrib_domain:
            vales = pool['product.product'].search_read(cr, uid, attrib_domain, ['product_tmpl_id'])
            domain += [('id', 'in',[x['product_tmpl_id'][0] for x in vales])]


        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = product_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=ppg, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)
        attributes_obj = request.registry['product.attribute']
        if product_ids:
            attributes_ids = attributes_obj.search(cr, uid, [('attribute_line_ids.product_tmpl_id', 'in', product_ids)], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool['res.users'].browse(cr, uid, uid, context=context).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        sb_brand_ids = pool["sb.brands"].search_read(cr, uid, [],['name'] ,context=context)
        product_wheel_size = request.env['sb.model.size'].sudo().search([])
        product_vehicle_model = request.env['sb.brands'].sudo().search([])
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products, ppg),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib',i) for i in attribs]),
            'sb_brand_ids': sb_brand_ids,
            'p_wheel_size': product_wheel_size,
            'p_vehicle_model': product_vehicle_model,
            'left_search_attrib':left_search_attrib,
            'main_search_attrib': main_search_attrib,
            'main_search_value': main_search_value,

        }
        if category:
            values['main_object'] = category


        return request.website.render("website_sale.products", values)

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        cr, uid, context = request.cr, request.uid, request.context
        email_act = None
        sale_order_obj = request.registry['sale.order']

        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.registry['payment.transaction'].browse(cr, uid, transaction_id, context=context)

        if sale_order_id is None:
            order = request.website.sale_get_order(context=context)
        else:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done']:
            if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.with_context(dict(context, send_email=True)).action_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(cr, SUPERUSER_ID, [order.id], context=request.context)

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)

        return request.redirect('/shop/confirmation')


class WebsiteRequestCallback(http.Controller):
    @http.route('/fawheels/get_model', type='json', auth="public", website=True)
    def post_bump(self, model_id, **kwarg):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context, request.registry
        model_ids = pool['sb.vehicle.model'].search_read(cr, uid, [('brand_id', '=', model_id)], ['name'])
        return model_ids




    @http.route('/fawheels/get/partner', type='json', auth="public", website=True)
    def get_partner_desc_fa(self, email, **kwarg):
        feilds = ['name','house_number', 'street', 'street2', 'city', 'phone', 'postcode', 'country_id','mobile']
        return request.env['res.partner'].sudo().search_read([('email','=', email)], feilds, limit=1)


    @http.route('/fawheels/products', type='json', auth="public", website=True)
    def get_model_products(self, model_id, brand_id, size_id, **kwarg):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context, request.registry
        products = pool['product.product'].search_read(cr, uid, [('make_id', '=', model_id), ('model_id', '=', brand_id), ('size_id', '=', size_id)], [])
        return products


    @http.route('/fawheels/postcode', type='json', auth="public", website=True)
    def get_address_postcode(self, postcode, **kwarg):
        row = None
        value = {}
        try:
            if not postcode: return
            connection = (psycopg2.connect("dbname='postcode' user='ubuntu' host='52.30.183.134' password='admin123'"))
            cr = connection.cursor()
            cr.execute("SELECT postcode1,street,town,county from POSTCODE where postcode='%s'" % (postcode))
            row = cr.fetchone()

        except Exception as e:
            pass
        if row:
            value['zip'] = row[0]
            value['street'] = row[1].title() if row[1] else None
            value['city'] = row[2].title() if row[2] else None
        return value

    @http.route('/website_request_callback', type='http', auth="public", methods=['POST'], website=True)
    def website_request_callback(self, **kwargs):
        if kwargs.get('name') and kwargs.get('phone') and kwargs.get('email_from'):
            partner_id = request.env['res.partner'].sudo().create({'name': kwargs.get('name'),
                                                                   'phone': kwargs.get('phone'),
                                                                   'email': kwargs.get('email_from')})
        # if kwargs.get('name') and kwargs.get('phone'):
            cem_lead = request.env['crm.lead'].sudo().create({'partner_id': partner_id.id,
                                                   'name': 'Plan to rework ' + kwargs.get('no_of_wheels_to_rework') + ' wheels',
                                                   'phone': partner_id.phone,
                                                   'email_from': partner_id.email,
                                                   'description': "No. of wheels to rework: " + kwargs.get('no_of_wheels_to_rework') + "\nWheel Size: " + kwargs.get('car_wheel_size') + "\nProducts: " + kwargs.get('products')
                                                 })
            template = request.env['ir.model.data'].sudo().get_object('fawheels', 'auto_generate_email_fawheels_crm')
            template.send_mail(cem_lead.id, force_send=True)

        return request.redirect('/')

    @http.route('/request_a_quote', type='http', auth="public", methods=['POST'], website=True)
    def website_request_a_quote(self, **kwargs):
        country_id = False
        make_id = False
        model_id = False
        size_id = False
        hear_about_us = False
        res_partner = request.env['res.partner'].sudo()
        
        ir_attachment = request.env['ir.attachment'].sudo()
        if kwargs.get('country'):
            country_id = int( kwargs.get('country'))
        if kwargs.get('car_brand'):
            make_id = int(kwargs.get('car_brand'))
        if kwargs.get('car_model'):
            model_id = int(kwargs.get('car_model'))
        if kwargs.get('request_car_size'):
            size_id = int(kwargs.get('request_car_size'))
        if kwargs.get('hear_about_us') and kwargs.get('hear_about_us') != '0':
            hear_about_us = kwargs.get('hear_about_us')

        user = res_partner.search([('email','=', kwargs.get('email'))], limit=1)
        user_values = {
                        'name': kwargs.get('firstname'),
                        'email': kwargs.get('email'),
                        'house_number': kwargs.get('house_number'),
                        'street': kwargs.get('street'),
                        'city': kwargs.get('city'),
                        'street2': kwargs.get('street2'),
                        'mobile': kwargs.get('phone'),
                        'postcode': kwargs.get('postcode'),
                        'country_id': country_id,
                    }
        if len(user) == 0:
            user = request.env['res.partner'].sudo().create(user_values)
        else:
            user.write(user_values)

        values = {
            'partner_id': user.id,
            'vehicle_reg': kwargs.get('vehicle_reg'),
            'no_of_wheels': kwargs.get('no_of_wheels') or '',
            'finishing': kwargs.get('finish') or fawheels,
            'description_website': kwargs.get('additional_info'),
            'method_of_delivery': kwargs.get('method_of_delivery') or False,
            'booking_date': kwargs.get('booking_date') or False,
            'size_id': size_id
        }


        sale_order = request.env['sale.order'].sudo().create(values)
        price_unit = None
        if not kwargs.get('products', False):
            return request.website.render('fawheels.request_get_back_to_you')

        order_line = {
            'name' :  "New Quotation",
            'order_id': sale_order.id,
            'product_id': int(kwargs.get('products')),
            'product_uom_qty':  int(kwargs.get('no_of_wheels')),
            'product_uom' : 1,
            'price_unit': price_unit,
            'service_sale_type':'refurbish',
            'sb_type':'services',
        }
        
        sale_order_line = request.env['sale.order.line'].sudo().create(order_line)
        template = request.env['ir.model.data'].sudo().get_object('fawheels', 'auto_generate_email_fawheels')
        template.send_mail(sale_order.id, force_send=True)

        ufile  = kwargs.get('pic_upload')
        attachment_id = ir_attachment.create({
                'name': ufile.filename,
                'datas': base64.encodestring(ufile.read()),
                'datas_fname': ufile.filename,
                'res_model': "sale.order",
                'res_id': int(sale_order.id)
            })
        return request.website.render('fawheels.request_get_back_to_you')



    @http.route('/request_package_size', type='json', auth="public", website=True)
    def request_package_size(self, size_id, **post):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context, request.registry
        products = pool['product.product'].search_read(cr, uid, [('sb_type', '=', 'services'), ('service_sale_type', '=', 'refurbish'), ('size_id', '=', size_id)], ['name'])
        return products

    @http.route('/is_callback_request', type='json', auth="public", website=True)
    def is_callback_request(self, email_id, **post):
        email_present = request.env['res.partner'].search([('email', '=', email_id)], limit=1)
        if email_present:
            vals = {'cust_name': email_present.name, 'cust_email': email_present.email}
            if email_present.phone:
                vals.update({'cust_phone': email_present.phone})
            return vals
        return False

    @http.route('/fawheels/fetch_get_products', type='json', auth="public", website=True)
    def quick_quote_get_products(self, wheel_size):
        products = request.env['product.product'].sudo().search([('sb_type', '=', 'services'),
                                                                 ('service_sale_type', '=', 'refurbish'),
                                                                 ('size_id.name', '=', int(wheel_size))])
        prod_ids = []
        for prod in products:
            prod_ids.append({'id': prod.id, 'name': prod.name})
        return prod_ids
