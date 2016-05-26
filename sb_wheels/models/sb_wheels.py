#-*- coding:utf-8 -*-
##############################################################################
#
#    SnippetBucket, MidSized Business Application Solution
#    Copyright (C) 2013-2014 http://snippetbucket.com/. All Rights Reserved.
#    Email: snippetbucket@gmail.com, Skype: live.snippetbucket
#    
##############################################################################

from datetime import datetime, timedelta
from openerp import api, fields, models, _

class sb_wheels_width(models.Model):
    _name = "sb.wheels.width"
    _description = "sb.wheels.width"
    
    name = fields.Char(string= 'Min Width')
    max = fields.Char(string= 'Max Width')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            title = rec['name']
            if rec['max']:
                title =  "%s - %s" % (title, rec['max'])
            res.append((rec['id'], title))
        return res

class sb_wheels_height(models.Model):
    _name = "sb.wheels.height"
    _description = "sb.wheels.height"
    
    name = fields.Char(string = 'Height')
    
class sb_wheels_speed(models.Model):
    _name = "sb.wheels.speed"
    _description = "sb.wheels.speed"
  
    name = fields.Char(string = 'Speed')

class sb_wheels_diameter(models.Model):
    _name = "sb.wheels.diameter"
    _description = "sb.wheels.diameter"

    name = fields.Char(string = 'Min Diameter')
    max = fields.Char(string = 'Max Diameter')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            title = rec['name']
            if rec['max']: title =  "%s - %s" % (rec['name'], rec['max'])
            res.append((rec['id'], title))
        return res


class sb_wheels_offset(models.Model):
    _name = "sb.wheels.offset"
    _description = "sb.wheels.offset"

    name = fields.Char(string ='Min Offset')
    max = fields.Char(string = 'Max Offset')
    
    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            title = rec['name']
            if rec['max']: title =  "%s - %s" % (rec['name'], rec['max'])
            res.append((rec['id'], title))
        return res


class sb_wheels_pcd(models.Model):
    _name = "sb.wheels.pcd"
    _description = "sb.wheels.pcd"
    
    name = fields.Char(string = 'PCD')

class sb_wheels_color(models.Model):
    _name = "sb.wheels.color"
    _description = "sb.wheels.color"

    name = fields.Char('Colour')


class sb_brands(models.Model):
    _name = "sb.brands"
    _description = "sb.brands"

    name = fields.Char(string ='Name', required=True)
    logo = fields.Binary(string = 'Logo')
    website = fields.Char(string = 'Website')
    _sql_constraints = [
        ('brand_name_uniq', 'unique (name)', 'Name must be unique!')
    ]

class sb_vehicle_model(models.Model):
    _name = "sb.vehicle.model"
    _description = "sb.vehicle.model"
    
    name = fields.Char(string = 'Name', required=True)
    image = fields.Binary(string ='Image')
    make_year = fields.Char(string = 'Make Year')
    wheels = fields.Char(string = 'Wheels')
    wheels_code = fields.Char(string = 'Wheels Code')
    number = fields.Char(string = 'Number')
    color = fields.Char(string = 'Color')
    fuel_type = fields.Char(string ='Fuel Typ')
    transmission_type = fields.Char(string = 'Transmission')
    brand_id = fields.Many2one('sb.brands', string = 'Brand Name', required=True)

    _sql_constraints = [
        ('model_name_uniq', 'unique (name)', 'Name must be unique!')
    ]

class sb_order_note(models.Model):
    _name = "sb.order.note"
    _description = "sb.order.note"

    name = fields.Char(string = 'Name')
    date = fields.Char(string = 'Date', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    user_id = fields.Many2one('res.users', string = 'User', default=lambda self: self.env.user)
    sale_id = fields.Many2one('sale.order', string = 'Sale Order')

class sb_vehicle_tag(models.Model):
    _name = "sb.vehicle.tag"
    _description = "sb.vehicle.tag"

    name = fields.Char(string = 'Tag Wheel Number', required=True, default ="/" )
    type = fields.Selection([('fl','Front Left'),('fr','Front Right'),('rl','Rear Left'),('rr','Rear Right'),('ex','Spare Wheel'),], string = 'Type', required=True)
    external_no = fields.Char(string = 'External Number')
    barcode_no = fields.Char(string = 'Barcode Number')
    date = fields.Char(string = 'Date', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    product_id = fields.Many2one('product.product', string='Product', required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    sale_id = fields.Many2one('sale.order', string='Sale order')
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].get('sb.vehicle.code') or '/'
        res = super(sb_vehicle_tag, self).create(vals)
        return res


class sb_parts_restock(models.Model):
    _name = "sb.parts.restock"
    _description = "sb.parts.restock"

    name = fields.Char(sting = 'Part name')
    ref = fields.Char(string = 'Ref.')
    qty = fields.Integer(string = 'Quality ')
    status = fields.Selection([('a','Normal'),('b','Already Damage'),('c','Damage During Stock')], string = 'status', defult ='a', required=True)
    image = fields.Binary(string = 'Image')
    sale_id = fields.Many2one('sale.order', string = 'Sale order')
    date = fields.Char(string = 'Date ', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    user_id = fields.Many2one('res.users', string = 'User', default=lambda self: self.env.user)

class sb_vehicle_inspection(models.Model):
    _name = "sb.vehicle.inspection"
    _description = "sb.vehicle.inspection"

    name = fields.Char(string = 'Topic')
    comment = fields.Text(string = 'Comments')
    date = fields.Char(string = 'Date', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    image = fields.Binary(string = 'Image') 
    user_id = fields.Many2one('res.users', string ='User', default=lambda self: self.env.user)
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line')

    
class sb_onsite_images(models.Model):

    _name = "sb.onsite.images"
    _description = "sb.onsite.images"
    
    name = fields.Char(string = 'Title')
    user_id = fields.Many2one('res.users', string = 'User', default=lambda self: self.env.user)
    date =  fields.Char(string = 'Date ', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    kindof = fields.Selection([('before','Before Service'), ('after','After Service'), ('onsite','Onsite Image')], string = 'Kind Of')
    image  = fields.Binary(string ='Image')
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line')
    
class sb_before_images(models.Model):

    _name = "sb.before.images"
    _description = "sb.before.images"
    
    name = fields.Char(string='Title')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    date = fields.Char(string ='Date ', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    image = fields.Binary(string= 'Image') 
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line')

class sb_after_images(models.Model):

    _name = "sb.after.images"
    _description = "sb.after.images"
    
    name = fields.Char(string = 'Title')
    user_id = fields.Many2one('res.users', string ='User', default=lambda self: self.env.user)
    date = fields.Char(string = 'Date ', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    image = fields.Binary('Image') 
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line')
    

class sb_exchange_our_images(models.Model):

    _name = "sb.exchange.our.images"
    _description = "sb.exchange.our.images"
    
    name = fields.Char(string = 'Title')
    user_id = fields.Many2one('res.users', string = 'User', default=lambda self: self.env.user)
    date = fields.Char(string = 'Date', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    image = fields.Binary(string = 'Image')
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line')
    

class sb_exchange_their_images(models.Model):

    _name = "sb.exchange.their.images"
    _description = "sb.exchange.their.images"
    
    name = fields.Char(string ='Title')
    product_id = fields.Many2one('product.product', string = 'Product')
    wheel_type = fields.Selection([('front','Front'),('rear','Rear'),('set4','Set 4'),('set5','Set 5')], string = 'Wheel Type', required=False, help="Front, Rear, Set of 4 (2 Front& 2 Rear), Set of 5 (all the wheel, front/rear  3 front, 2 rear)")
    qty = fields.Integer(string = 'Quantity ', help='')
    image =  fields.Binary(string = 'Image')
    date =  fields.Char(string = 'Date', default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    user_id = fields.Many2one('res.users', string = 'User', default=lambda self: self.env.user)
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line')
    status = fields.Selection([('a','Draft'),('b','ReStocked')], 'Status', required=False, default = 'a')
    partner_id =  fields.Many2one("res.partner", string = "Customer")
    
    def process_refurb_stock(self, cr, uid, ids, context=None):
        product_product = self.pool.get('product.product')
        for ex in self.browse(cr, uid, ids, context=context):
            if ex.status == "a":
                product_id = product_product.browse(cr, uid, ex.product_id.id, context=context)
                product_product.write(cr, uid, product_id.id, {'unfinish_stock': product_id.unfinish_stock + ex.qty}, context=context)
                self.write(cr, uid, ex.id, {'status': 'b'}, context=context)


class sb_model_size(models.Model):
    _name = "sb.model.size"
    _description = "sb.model.size"

    name = fields.Char(string = 'Size', required=True)

    _sql_constraints = [
        ('size_name_uniq', 'unique (name)', 'Name must be unique!')
    ]


class sb_model_style(models.Model):
    _name = "sb.model.style"
    _description = "sb.model.style"

    name = fields.Char(string = 'Style', required=True)
    model_id = fields.Many2one('sb.vehicle.model', string = 'Vehicle Model')

class sb_model_type(models.Model):
    _name = "sb.model.type"
    _description = "sb.model.type"

    name = fields.Char(string = 'Type', required=True)
    model_id = fields.Many2one('sb.vehicle.model', string = 'Vehicle Model')

class sb_product_package(models.Model):
    _name = "sb.product.package"
    _description = "sb.product.package"

    name = fields.Char(string = 'Package Name', required=True)
    tyre_provision = fields.Selection([('with_tyre','With Tyre'),('without_tyre','Without Tyre'), ], 'Tyer Provision')
    caronsite = fields.Boolean(string ='Car Onsite')
    donorwheel = fields.Boolean(string = 'Donor Wheels Provided')
    donorwheel_charge = fields.Float(string = 'Donor Wheel Charge', help="")
    service_front_1unit = fields.Float(string ='Front 1 Unite', help="")
    service_back_1unit = fields.Float(string = 'Back 1 Unite', help="")
    service_front_pair  = fields.Float(string = 'Front Pair')
    service_back_pair = fields.Float(string = 'Back Pair')
    service_front_set4 = fields.Float(string = 'Front 4 Set ')
    service_front_set5 =  fields.Float(string = 'Front 5 Set')
    process_ids = fields.One2many('sb.job.process', 'product_package_id', string='Refurbish Process', copy=True)


class sb_product_finish(models.Model):
    _name = "sb.product.finish"
    _description = "Product Finish"

    name = fields.Char("Process Name")
    package_id = fields.Many2one('sb.product.package', string ='Package', required=True)
    sale_line_id = fields.Many2one('sale.order', string = 'Sale order line', required=True)
    from_product = fields.Many2one('product.product', string="Unifinished Product", required=True)
    to_product = fields.Many2one('product.product', string="Finished Product", required=True)
    quantity = fields.Integer("Quantity")
    unfinish_stock = fields.Integer("Unfinish Stock", related="from_product.unfinish_stock")
    partner_id =  fields.Many2one("res.partner", string = "Customer", related="sale_line_id.partner_id")
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())


    @staticmethod
    def _get_default_job_line(order):
        job_line = {
            'sale_order_id' : order.sale_line_id.id,
            'customer_id' : order.sale_line_id.partner_id.id,
            'make_id' : order.to_product.make_id.id,
            'model_id' : order.to_product.model_id.id,
            'vehicle_reg' : order.sale_line_id.vehicle_reg,
            'style_id' : order.to_product.style_id.id,
            'size_id' : order.to_product.size_id.id,
            'only_refurb_order_id': order.id,
            'is_exchange': True
        }
        return job_line

    @staticmethod
    def _get_default_job(order, sale_job_id):
        job = {
            'main_job_id': sale_job_id,
            'customer_id': order.sale_line_id.partner_id.id,
            'sale_order_id': order.sale_line_id.id,
            'booking_date' : order.sale_line_id.booking_date,
            'collection_date' : order.sale_line_id.collection_date,
            'booking_ready' : False,
            'product_id' : order.to_product.id,
            'product_package_id' : order.package_id.id,
            'make_id' : order.to_product.make_id.id,
            'model_id' : order.to_product.model_id.id,
            'vehicle_reg' : order.sale_line_id.vehicle_reg,
            'style_id' : order.to_product.style_id.id,
            'size_id' : order.to_product.size_id.id,
            'only_refurb_order_id': order.id
        }
        return job

    @staticmethod
    def _get_job_line(process, line_dict):
        tags = [ t.id for t in process.tag_ids]
        tagsname = ', '.join([ t.name for t in process.tag_ids])
        line_dict.update({
             'tag_ids':[(6,0, tags)],
             'sequence': process.sequence,
             'subprocess_id': process.subprocess_id.id,
             'name': process.name,
             'tag_title': tagsname,
             'product_package_id': process.product_package_id.id,
             'not_include': process.not_include
            })
        return line_dict

    @api.multi
    def process_refurb_stock(self):
        sb_job_order =  self.env['sb.job.order']
        sb_job_item =  self.env['sb.job.item']
        sale_job_order = self.env['sale.job.order']
        sale_job_id = None

        for res in self:
            sale_job_id = sale_job_order.search([('sale_order_id', '=', res.sale_line_id.id)])
            if not sale_job_id.id:sale_job_id = None
            if sale_job_id is None:
                sale_job_id = sale_job_order.create({
                                'sale_order_id': res.sale_line_id.id,
                                'is_exchange': True,
                                'only_refurb_order_id':res.id,
                        })
            for qty in range(0, res.quantity):
                job_left =  self._get_default_job(res, sale_job_id.id)
                job_left_id = sb_job_order.create(job_left)
                for process in res.package_id.process_ids:
                    job_right_front_line = self._get_default_job_line(res)
                    self._get_job_line(process, job_right_front_line)
                    job_right_front_line.update({
                        'wheels_perticulars': 'Rigt Front',
                        'job_order_id': job_left_id.id,
                        'main_process': process.main_process, 
                        })
                    sb_job_item.create(job_right_front_line)

    @api.onchange('to_product','from_product','sale_line_id')
    def change_name_of_order(self):
        name = ""
        if self.to_product.name:
            name = name  + self.to_product.name
        if self.from_product.name:
            name = name + "/" + self.from_product.name
        if self.sale_line_id.name:
            name = name + "/" + self.sale_line_id.name
        self.name =  name