import logging
import requests
import json
from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.osv import osv
from openerp.tools import float_compare


_logger = logging.getLogger(__name__)


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    left_front = fields.Boolean(string = 'Left Front')
    left_back = fields.Boolean(string = 'Left Back')
    right_front = fields.Boolean(string = 'Right Front')
    right_back = fields.Boolean(string = 'Right Back')
    spare_wheel = fields.Boolean(string = 'Spare Wheel')

    left_front_barcode = fields.Char(string = 'Left Front Code')
    left_back_barcode =  fields.Char(string = 'Left Back Code')
    right_front_barcode = fields.Char(string = 'Right Front Code')
    right_back_barcode =  fields.Char(string ='Right Back')
    spare_wheel_barcode = fields.Char(string = 'Spare Wheel Code')

    sb_type =  fields.Selection([('wheel','Wheel'),('tyre','Tyre'),('accessories','Accessories'),('services','Services')], string = 'Type', required=False)
    product_sale_type = fields.Selection([('sale','Sale'),('exchange','Exchange'), ], string = 'Product Sale Type', required=False)
    service_sale_type = fields.Selection([('refurbish','Refurbish'),('repair','Repair Service'), ('other_service','Other Services'),], string = 'Service Type', required=False)

    vehicle_reg = fields.Char(string = 'Vehicle Registration')
    make_id = fields.Many2one('sb.brands', string = 'Make')
    model_id = fields.Many2one('sb.vehicle.model', string = 'Model')
    size_id = fields.Many2one('sb.model.size', string = 'Wheel Size')
    style_id = fields.Many2one('sb.model.style', string = 'Wheel Style')
    type_id = fields.Many2one('sb.model.type', string = 'Wheel Type')
    package_id = fields.Many2one('sb.product.package', string = 'Package')
    
    
    wheel_width = fields.Many2one('sb.wheels.width', string = 'Width')
    wheel_height = fields.Many2one('sb.wheels.height', string = 'Height')
    wheel_speed = fields.Many2one('sb.wheels.speed', string = 'Speed')
    wheel_diameter = fields.Many2one('sb.wheels.diameter', string = 'Diameter')
    wheel_offset = fields.Many2one('sb.wheels.offset', string ='Offset')
    wheel_pcd = fields.Many2one('sb.wheels.pcd', string = 'PCD')
    wheel_color = fields.Many2one('sb.wheels.color', string = 'Color')
    
    by_filter = fields.Boolean(string = 'Filter Product By Vehicle Details', default = True)
    product_image = fields.Binary('Image',  attachment=True)
    default_code = fields.Char(string = 'Reference Number')
    

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(sale_order_line, self)._prepare_invoice_line(qty)
        res.update (
            {'dicount_type': self.dicount_type,
             'sb_type': self.sb_type,
             'product_sale_type': self.product_sale_type,
             'service_sale_type': self.service_sale_type,
             'by_filter': self.by_filter,
             'vehicle_reg': self.vehicle_reg,
             'make_id': self.make_id.id,
             'model_id': self.model_id.id,
             'product_image': self.product_image,
             'default_code': self.default_code,
             'left_front': self.left_front,
             'left_back': self.left_back,
             'right_front': self.right_front,
             'right_back': self.right_back,
             'spare_wheel': self.spare_wheel,
             'size_id': self.size_id.id,
             'style_id': self.style_id.id,
             'type_id': self.type_id.id,
             'wheel_width': self.wheel_width.id,
             'wheel_height': self.wheel_height.id,
             'wheel_speed': self.wheel_speed.id,
             'wheel_diameter': self.wheel_diameter.id,
             'wheel_offset': self.wheel_offset.id,
             'wheel_pcd': self.wheel_pcd.id,
             'wheel_color': self.wheel_color.id,
             
             })
        return res

    @api.onchange('left_front','right_front','left_back','right_back','spare_wheel', 'product_uom_qty')
    def _wheel_unit(self):
        if self.sb_type in ('tyre', 'wheel','services'):
            if self.product_sale_type in ('exchange','sale') or self.service_sale_type in ('repair','refurbish'):
                qty = 0.0
                if self.spare_wheel:
                   self.left_front = True
                   self.right_front = True
                   self.left_back = True
                   self.right_back = True
                   qty = 5.0
                else:
                    if self.left_front:
                       qty += 1.0
                    if self.right_front:
                       qty += 1.0
                    if self.left_back:
                       qty += 1.0
                    if self.right_back:
                       qty += 1.0
                self.product_uom_qty = qty

    def getparseddata(self, xmldata):
        from . import xmltodict
        import json
        o = xmltodict.parse(xmldata.replace("\n",'').replace("  ",''))
        return json.loads(json.dumps(o))

        o = xmltodict.parse(xmldata.replace("\n",'').replace("  ",''))
        return json.loads(json.dumps(o))

    @api.multi
    @api.onchange('vehicle_reg')
    def onchange_vehicle_reg(self):
        res = {}
        if self.vehicle_reg:
            _brand = self.env['sb.brands']
            _model = self.env['sb.vehicle.model']
            try:
                r  = requests.get('http://www.hpixml.com/servlet/HpiGate1_0?efxid=0437730&password=bear&initials=xx&function=SEARCH&vrm=%s&XML=YES&product=HPI11&devicetype=XM'% self.vehicle_reg.replace(" ", ""))

                dvla_data = self.getparseddata(r.content.replace('<?xml version="1.0"?>', ''))

                basic = dvla_data.get('HPICheck_Query').get('Basic', {})
                Additional = dvla_data.get('HPICheck_Query').get('Additional', {})
                if basic.get('Make', False):

                    wheels_make = basic.get('Make')
                    wheels_model = basic.get('Model')

                    wheel_code = Additional.get('Wheelplan_code')
                    color =  basic.get('Colour')
                    model_code =  basic.get('Model_Code')
                    transmission =  basic.get('Transmission')
                    model_ids = _model.search([('name', '=', wheels_model)])

                    if not model_ids:
                        brand_ids = _brand.search([('name', '=', wheels_make)])
                        if not brand_ids:
                            create_brand = _brand.create({'name' : wheels_make})
                            res['make_id'] = create_brand
                        else:
                            res['make_id'] =  brand_ids.id
                        create_model = _model.create({
                                'name' : wheels_model,
                                'brand_id' : brand_ids.id if brand_ids else create_brand,
                                'make_year': Additional.get('Mfr_Year'),
                                'wheels_code': Additional.get('Wheelplan_code'),
                                'wheels': Additional.get('Wheelplan'), 
                                'color':  color, 
                                'fuel_type': basic.get('fuel'), 
                                'transmission_type':  basic.get('Transmission'),
                                'number': self.vehicle_reg,
                            })
                        res['model_id'] = create_model
                    else:
                        res['make_id'] = model_ids.brand_id.id 
                        res['model_id'] = model_ids.id
            except Exception as e:
                _logger.warning("Exception While Vehicle detail from http://www.hpixml.com %s", (e))
            self.update(res)

    @api.onchange('sb_type', 'product_sale_type', 'service_sale_type', 'make_id', 'model_id', 'size_id','style_id','type_id')
    def _on_change_wheel(self):
        domain = {'product_id': [("is_sub_product", "=", False)]}
        
        dom = []
        if self.sb_type:
             domain['product_id'].append(('sb_type','=',self.sb_type))
             
        if self.sb_type in ('wheel','tyre') and self.product_sale_type == 'sale':
             domain['product_id'].append(('service','=',True))
             
        if self.sb_type in ('wheel','tyre') and self.product_sale_type == 'exchange':
             domain['product_id'].append(('exchange_stock','=',True))
             self.service_sale_type = False
             
        if self.sb_type == 'services' and self.service_sale_type:
             domain['product_id'].append(('service_sale_type','=', self.service_sale_type))
             self.product_sale_type = False
        
        if self.sb_type == 'accessories':
            self.by_filter = False
        else:
            self.by_filter = True
        return { 'domain': domain }
    

    @api.onchange('product_id', 'left_front','right_front', 'right_back', 'left_back','left_front','spare_wheel')
    def product_id_change(self):
        result = super(sale_order_line, self).product_id_change()
        vals = {}

        #to check
        #prices = self.pool.get('product.product').read(cr, uid, product, [ ], context=context) 

        if self.size_id:
            self.name = "%s\nSize: %s"%(self.product_id.name , self.size_id.name)
        
        if self.style_id:
            self.name = "%s\nStyle: %s"%(self.name , self.style_id.name)
        
        if self.type_id:
            self.name = "%s\nType: %s"%(self.name , self.type_id.name)
        
        if self.product_id:
            vals['default_code'] = self.product_id.default_code
            vals['product_image'] = self.product_id.image_medium

        if self.product_id.package_id:
            vals['package_id'] = self.product_id.package_id.id

        front = 0
        back  = 0
        if self.left_front:
            front += 1
        if self.right_front:
            front += 1
        if self.left_back:
            back += 1
        if self.right_back:
            back += 1

        ## For Tyres

        if self.product_id and self.sb_type == 'tyre' and not self.product_sale_type:
            raise osv.except_osv('Missing Value', _("Fill Product Sale Type for Tyres."))
        
        if self.product_id and self.sb_type == 'tyre' and  self.product_sale_type == 'sale':
            vals['price_unit'] = 0.0
            if front + back == 4:
                vals['price_unit'] = self.product_id.sale_front_set5 / 5.0  if self.spare_wheel else self.product_id.sale_front_set4 / 4.0 
            elif front == 2:
                vals['price_unit'] = self.product_id.sale_front_pair / float(front)
            elif back == 2:
                vals['price_unit'] = self.product_id.sale_back_pair / float(back)
            elif front == 2 and back == 1 :
                vals['price_unit'] = self.product_id.sale_front_pair + self.product_id.sale_back_1unit/ 3.0
            elif front == 1 and back == 2 :
                vals['price_unit'] = (self.product_id.sale_front_1unit + self.product_id.sale_back_pair)/ 3.0
            if front == 1 and back != 2:
                vals['price_unit'] += self.product_id.sale_front_1unit
            if back  == 1 and front != 2:
                vals['price_unit'] += self.product_id.sale_back_1unit

            if front == 1 and back == 1:
                vals['price_unit'] = vals['price_unit'] / float(front+back)


        if self.product_id and  self.sb_type== 'tyre' and self.product_sale_type == 'exchange' :
            vals['price_unit'] = 0.0
            if front + back == 4:
                vals['price_unit'] = self.product_id.exchange_front_set5 / 5.0  if self.spare_wheel else self.product_id.exchange_front_set4 / 4.0 
            elif front == 2:
                vals['price_unit'] = self.product_id.exchange_front_pair / float(front)
            elif back == 2:
                vals['price_unit'] = self.product_id.exchange_back_pair / float(back)
            elif front == 2 and back == 1 :
                vals['price_unit'] = (self.product_id.exchange_front_pair + self.product_id.exchange_back_1unit)/ 3.0
            elif front == 1 and back == 2 :
                vals['price_unit'] = (self.product_id.exchange_front_1unit+self.product_id.exchange_back_pair)/ 3.0
            if front == 1 and back != 2:
                vals['price_unit'] += self.product_id.exchange_front_1unit
            if back  == 1 and front != 2:
                vals['price_unit'] += self.product_id.exchange_back_1unit

            if front == 1 and back == 1:
                vals['price_unit'] = vals['price_unit'] / float(front+back)
                
                
        ## For Wheels 


        if self.product_id and self.sb_type == 'wheel' and not self.product_sale_type:
            raise osv.except_osv('Missing Value', _("Fill Product Sale Type for Wheel."))
        
        if self.product_id and self.sb_type == 'wheel' and  self.product_sale_type == 'sale':
            vals['price_unit'] = 0.0
            if front + back == 4:
                vals['price_unit'] = self.product_id.sale_front_set5 / 5.0  if self.spare_wheel else self.product_id.sale_front_set4 / 4.0 
            elif front == 2:
                vals['price_unit'] = self.product_id.sale_front_pair / float(front)
            elif back == 2:
                vals['price_unit'] = self.product_id.sale_back_pair / float(back)
            elif front == 2 and back == 1 :
                vals['price_unit'] = self.product_id.sale_front_pair + self.product_id.sale_back_1unit/ 3.0
            elif front == 1 and back == 2 :
                vals['price_unit'] = (self.product_id.sale_front_1unit + self.product_id.sale_back_pair)/ 3.0
            if front == 1 and back != 2:
                vals['price_unit'] += self.product_id.sale_front_1unit
            if back  == 1 and front != 2:
                vals['price_unit'] += self.product_id.sale_back_1unit

            if front == 1 and back == 1:
                vals['price_unit'] = vals['price_unit'] / float(front+back)


        if self.product_id and  self.sb_type== 'wheel' and self.product_sale_type == 'exchange' :
            vals['price_unit'] = 0.0
            if front + back == 4:
                vals['price_unit'] = self.product_id.exchange_front_set5 / 5.0  if self.spare_wheel else self.product_id.exchange_front_set4 / 4.0 
            elif front == 2:
                vals['price_unit'] = self.product_id.exchange_front_pair / float(front)
            elif back == 2:
                vals['price_unit'] = self.product_id.exchange_back_pair / float(back)
            elif front == 2 and back == 1 :
                vals['price_unit'] = (self.product_id.exchange_front_pair + self.product_id.exchange_back_1unit)/ 3.0
            elif front == 1 and back == 2 :
                vals['price_unit'] = (self.product_id.exchange_front_1unit+self.product_id.exchange_back_pair)/ 3.0
            if front == 1 and back != 2:
                vals['price_unit'] += self.product_id.exchange_front_1unit
            if back  == 1 and front != 2:
                vals['price_unit'] += self.product_id.exchange_back_1unit

            if front == 1 and back == 1:
                vals['price_unit'] = vals['price_unit'] / float(front+back)

        if self.product_id and self.sb_type == 'services' and self.service_sale_type == 'refurbish' :
            vals['price_unit'] = 0.0
            if self.package_id:
                if front + back == 4:
                    vals['price_unit'] = self.package_id.service_front_set5 / 5.0  if self.spare_wheel else  self.package_id.service_front_set4 / 4.0 
                elif front == 2:
                    vals['price_unit'] = self.package_id.service_front_pair / float(front)
                elif back == 2:
                    vals['price_unit'] = self.package_id.service_back_pair / float(back)
                elif front == 2 and back == 1 :
                    vals['price_unit'] = (self.package_id.service_front_pair + self.package_id.service_back_1unit)/ 3.0
                elif front == 1 and back == 2 :
                    vals['price_unit'] = (self.package_id.service_front_1unit + self.package_id.service_back_pair)/ 3.0
                if front == 1 and back != 2:
                    vals['price_unit'] += self.package_id.service_front_1unit
                if back  == 1 and front != 2:
                    vals['price_unit'] += self.package_id.service_back_1unit

                if self.product_id.donor_wheels:
                    vals['price_unit'] = vals['price_unit'] + self.package_id.donorwheel_charge
                
                if front == 1 and back == 1:
                    vals['price_unit'] = vals['price_unit'] / float(front+back)
        
        if self.product_id:
            vals['wheel_width']    = self.product_id.wheel_width
            vals['wheel_height']   = self.product_id.wheel_height
            vals['wheel_speed']    = self.product_id.wheel_speed
            vals['wheel_diameter'] = self.product_id.wheel_diameter
            vals['wheel_offset']   = self.product_id.wheel_offset
            vals['wheel_pcd']      = self.product_id.wheel_pcd
            vals['wheel_color']    = self.product_id.wheel_color
            total_qty = float( front + back) + (1 if self.spare_wheel else 0)
            vals['product_uom_qty'] = total_qty or self.product_uom_qty
            


        self.update(vals)
        return result

class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _get_no_joborders(self):
        res = {}
        _jo = self.env['sb.job.order']
        for rec in self:
            rec.no_joborders = len(_jo.search([('sale_order_id','=',rec.id)]))

    source =  fields.Selection([('google','Google'),('facebook','Facebook'),('twitter','Twitter'),('instagram','Instagram'),('Flyer','Flyer'),
                            ('another','Another Client'),('dropin','Drop-In'),('searchengine','Search Engine'),('phone','Phone'),('web','Web'),('ebay','eBay'),('walkin','Walk-in'),
                  ('reference','Reference'),('others','Others'),], string = 'Source', required=False)
    source_note = fields.Char(string = 'Free Text')
    before_image_ids = fields.One2many('sb.before.images',  'sale_line_id', string ='Before Images')
    after_image_ids = fields.One2many('sb.after.images',   'sale_line_id', string = 'After Images')
    onsite_image_ids = fields.One2many('sb.onsite.images',   'sale_line_id', string = 'Onsite Images')
    exchange_our_image_ids = fields.One2many('sb.exchange.our.images',   'sale_line_id', string = 'Exchange Our')
    exchange_their_image_ids = fields.One2many('sb.exchange.their.images',   'sale_line_id', string ='Exchange Their')
    inspection_ids = fields.One2many('sb.vehicle.inspection',  'sale_line_id', string = 'Inspection')
    restock_ids = fields.One2many('sb.parts.restock',  'sale_id', string = 'ReStock')
    note_ids =  fields.One2many('sb.order.note',  'sale_id', string = 'Notes')
    wheel_tag_ids = fields.One2many('sb.vehicle.tag',  'sale_id', string = 'Wheels Tag')
    
    has_inspection = fields.Boolean(string = 'Inspection')
    has_images = fields.Boolean(string = 'Images')
    has_restock =  fields.Boolean(string = 'ReStock')
    has_refurb = fields.Boolean(string = 'Refurb/Repair')
    has_exchange =  fields.Boolean(string = 'Exchange')

    vehicle_reg = fields.Char(string = 'Vehicle Registration',)
    make_id = fields.Many2one('sb.brands', string = 'Make')
    model_id = fields.Many2one('sb.vehicle.model', string ='Model')
    size_id = fields.Many2one('sb.model.size', string = 'Wheel Size')
    booking_date =  fields.Datetime(string = 'Booking Date', help="Booking Date ( Wheels dropping)")
    est_complete_date =  fields.Datetime(string = 'Est  Completion Date', help="Est  Completion Date (JO Completion)")
    collection_date = fields.Datetime(string = 'Collection Date', help="Collection Date (Wheel fitting into the car)")
    no_joborders = fields.Integer(compute='_get_no_joborders', string='No. Job Orders ', store=False)
    no_of_wheels = fields.Char(string = 'Number of Wheels')
    description_website = fields.Text(string='Description of Online Quote')
    method_of_delivery = fields.Selection([
            ('1','Bring in my car (on site)'),
            ('2','Only wheels with tyres'),
            ('3','Only wheels no tyres')], string = 'Method of Delivery')

    finishing =  fields.Selection([('1', 'Standard Silver'),
        ('2', 'Super Silver'),
        ('3', 'Super Shiny Silver'),
        ('4', 'Sparkle Silver'),
        ('5', 'Black'),
        ('6', 'White'),
        ('7', 'Gold'),
        ('8', 'Smoked Chrome'),
        ('9', 'Hyper Silver'),
        ('10', 'I am not sure...'),
        ], string = "Finishing")
    
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()
        invoice_vals['vehicle_reg'] = self.vehicle_reg or False
        invoice_vals['make_id'] = self.make_id.id or False
        invoice_vals['model_id'] = self.model_id.id or False
        return invoice_vals
    
    @api.multi
    def name_get(self):
        if not self.env.context.get('jobscalendar',False):
            return super(sale_order, self).name_get()
        res = []
        _jo = self.env['sb.job.order']
            
        services = self.read(['name','vehicle_reg'])
        for service in services:
            title =  "%s (%s) / %s " % (service['name'],len(_jo.search([('sale_order_id','=',service['id'])])), service['vehicle_reg'])
            res.append((service['id'], title))
        return res
    @api.multi
    def create_sale_order_line(self, domain, default, so):
        product_id = self.env['product.product'].search(domain)
        order_id = so.order_id.id
        if len(product_id) > 0:
            default['product_id'] = product_id.id
            so.copy(default=default)
    @api.multi
    def process_sale_order(self):
        for sale_order_line in self.order_line:
            if sale_order_line.sb_type in ['tyre', 'wheel'] and sale_order_line.product_id.has_sub_product:
                if sale_order_line.left_front and sale_order_line.right_front:
                    self.create_sale_order_line([
                        ('parent_id','=',sale_order_line.product_id.id),
                        ('is_sub_product','=',True),
                        ('sub_product_type','=', 'front')
                        ], {'product_uom_qty':2 , 
                            'order_id' : sale_order_line.order_id.id
                            },sale_order_line)
                    
                else:
                    if sale_order_line.left_front or sale_order_line.right_front:
                        self.create_sale_order_line([
                            ('parent_id','=',sale_order_line.product_id.id),
                            ('is_sub_product','=',True),
                            ('sub_product_type','=', 'front')
                            ], {'product_uom_qty':1 , 
                                'order_id' : sale_order_line.order_id.id
                                }, sale_order_line)

                if sale_order_line.left_back and sale_order_line.right_back:
                    self.create_sale_order_line([
                        ('parent_id','=',sale_order_line.product_id.id),
                        ('is_sub_product','=',True),
                        ('sub_product_type','=', 'back')
                        ], {'product_uom_qty':2 , 
                            'order_id' : sale_order_line.order_id.id
                            }, sale_order_line)

                else:
                    if sale_order_line.left_back or sale_order_line.right_back:
                        self.create_sale_order_line([
                        ('parent_id','=',sale_order_line.product_id.id),
                        ('is_sub_product','=',True),
                        ('sub_product_type','=', 'back')
                        ], {'product_uom_qty':1 , 
                            'order_id' : sale_order_line.order_id.id
                            }, sale_order_line)

                if sale_order_line.spare_wheel:
                    self.create_sale_order_line([
                        ('parent_id','=',sale_order_line.product_id.id),
                        ('is_sub_product','=',True),
                        ('sub_product_type','=', 'spare_wheels')
                        ], {'product_uom_qty':1 , 
                            'order_id' : sale_order_line.order_id.id
                            }, sale_order_line)
                sale_order_line.unlink()
    @api.multi
    def view_joborders(self):
        domain = [('sale_order_id','=', self.id)]
        sale_job_order = self.env['sale.job.order']
        job_state = sale_job_order.search(domain)
        action = {}
        
        if job_state.state.name ==  "Draft":
            action = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sale_job_order_action1')
        if job_state.state.name ==  "Work In Progess":
            action = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sale_job_order_action2')
        if job_state.state.name ==  "Ready To Delivery":
            action = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sale_job_order_action3')
        if job_state.state.name ==  "Job Done":
            action = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sale_job_order_action4')
        
        context = {
                   'lang': self._context.get('lang'),
                   'tz': self._context.get('tz'), 
                   'uid': self._context.get('uid'),
                   'default_sale_order_id': self.id,
                   'default_customer_id': self.partner_id.id,
                   }
        action['context'] = context
        action['domain'] = domain
        return action
        

#     @api.multi
#     def action_ship_create(self):
#         """Create the required procurements to supply sales order lines, also connecting
#         the procurements to appropriate stock moves in order to bring the goods to the
#         sales order's requested location.
#  
#         :return: True
#         """
#         procurement_obj = self.env['procurement.order']
#         sale_line_obj = self.env['sale.order.line']
#         for order in self:
#             proc_ids = []
#             vals = self._prepare_procurement_group(order)
#             if not order.procurement_group_id:
#                 group_id = self.env["procurement.group"].create(vals)
#                 order.write({'procurement_group_id': group_id})
#  
#             for line in order.order_line:
#                 #Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
#                 if line.procurement_ids:
#                     #first check them to see if they are in exception or not (one of the related moves is cancelled)
#                     procurement_obj.check([x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
#                     line.refresh()
#                     #run again procurement that are in exception in order to trigger another move
#                     proc_ids += [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
#                     procurement_obj.reset_to_confirmed(proc_ids)
#                 elif sale_line_obj.need_procurement([line.id]):
#                     if (line.state == 'done') or not line.product_id:
#                         continue
#                          
#                     if line.sb_type not in ['wheel']:
#                         vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
#                         proc_id = procurement_obj.create(vals)
#                         proc_ids.append(proc_id)
#                         # continue, here wheel or not tyre so directly process them.
#                         continue
#                          
#                     if line.left_front:
#                         wheel_type = 'front'
#                         vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
#                         vals['wheel_type'] = wheel_type
#                         vals['product_qty'] = 1.0
#                         proc_id = procurement_obj.create(vals)
#                         proc_ids.append(proc_id)
#                     if line.right_front:
#                         wheel_type = 'front'
#                         vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
#                         vals['wheel_type'] = wheel_type
#                         vals['product_qty'] = 1.0
#                         proc_id = procurement_obj.create(vals)
#                         proc_ids.append(proc_id)
#                     if line.left_back:
#                         wheel_type = 'rear'
#                         vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
#                         vals['wheel_type'] = wheel_type
#                         vals['product_qty'] = 1.0
#                         proc_id = procurement_obj.create(vals)
#                         proc_ids.append(proc_id)
#                     if line.right_back:
#                         wheel_type = 'rear'
#                         vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
#                         vals['wheel_type'] = wheel_type
#                         vals['product_qty'] = 1.0
#                         proc_id = procurement_obj.create(vals)
#                         proc_ids.append(proc_id)
#                     if line.spare_wheel:
#                         wheel_type = 'front'
#                         vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
#                         vals['wheel_type'] = wheel_type
#                         vals['product_qty'] = 1.0
#                         proc_id = procurement_obj.create(vals)
#                         proc_ids.append(proc_id)
#  
#             #Confirm procurement order such that rules will be applied on it
#             #note that the workflow normally ensure proc_ids isn't an empty list
#             procurement_obj.run(proc_ids)
#  
#             #if shipping was in exception and the user choose to recreate the delivery order, write the new status of SO
#             if order.state == 'shipping_except':
#                 val = {'state': 'progress', 'shipped': False}
#  
#                 if (order.order_policy == 'manual'):
#                     for line in order.order_line:
#                         if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
#                             val['state'] = 'manual'
#                             break
#                 order.write(val)
#         return True

    @staticmethod
    def _get_default_job(order, line, sale_job_id):
        job = {
            'main_job_id': sale_job_id,
            'customer_id': order.partner_id.id,
            'sale_order_id': order.id,
            'booking_date' : order.booking_date,
            'collection_date' : order.collection_date,
            'booking_ready' : False,
            'product_id' : line.product_id.id,
            'product_package_id' : line.package_id.id,
            'make_id' : line.make_id.id,
            'model_id' : line.model_id.id,
            'vehicle_reg' : line.vehicle_reg,
            'style_id' : line.style_id.id,
            'size_id' : line.size_id.id,
            'sale_order_line_id' : line.id,
        }
        if line.service_sale_type == "repair":
            job['is_repair'] = True
        return job

    @staticmethod
    def _get_default_job_line(order, line):
        job_line = {
            'sale_order_id' : order.id,
            'customer_id' : order.partner_id.id,
            'make_id' : line.make_id.id,
            'model_id' : line.model_id.id,
            'vehicle_reg' : line.vehicle_reg,
            'style_id' : line.style_id.id,
            'size_id' : line.size_id.id,
        }
        return job_line

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
    def action_confirm(self):
        res = super(sale_order, self).action_confirm()
        
        sb_job_order =  self.env['sb.job.order']
        sb_job_item =  self.env['sb.job.item']
        sale_job_order = self.env['sale.job.order']
        sale_job_id = None
        is_repair = False
        for order in self:
            for ex in order.exchange_their_image_ids:
                ex.product_id.write({'unfinish_stock': ex.product_id.unfinish_stock + ex.qty})
                ex.write({'status':'b'})


            for line in self.order_line:
                if line.sb_type == 'services' and line.service_sale_type in ['refurbish', 'repair']:
                    if line.service_sale_type == 'repair':
                        is_repair = True
                    if not self.product_id:
                        raise osv.except_osv('Information Required', _("Select Product"))
                    if not line.package_id:
                        raise osv.except_osv('Information Required', _("Item line with refurbish/repair package not found."))
                    if not line.package_id.process_ids:
                        raise osv.except_osv('Information Required', _("Item line with refurbish/repair package had process not found."))

                    if not line.package_id.process_ids:
                        raise osv.except_osv('Required things missing', _("In Refurbish Package did not hold processes."))
                    if not (line.spare_wheel or line.left_front or line.right_front or line.left_back or line.right_back):
                        raise osv.except_osv('Required things missing', _("Kindly select wheel, least one."))

            for line in self.order_line:
                if line.sb_type == 'services' and line.service_sale_type in ['refurbish', 'repair']:
                    if not self.product_id:
                        raise osv.except_osv('Information Required', _("Select Product"))
                    if not line.package_id:
                        raise osv.except_osv('Information Required', _("Item line with refurbish/repair package not found."))
                    if not line.package_id.process_ids:
                        raise osv.except_osv('Information Required', _("Item line with refurbish/repair package had process not found."))

                    if not line.package_id.process_ids:
                        raise osv.except_osv('Required things missing', _("In Refurbish Package did not hold processes."))
                    if not (line.spare_wheel or line.left_front or line.right_front or line.left_back or line.right_back):
                        raise osv.except_osv('Required things missing', _("Kindly select wheel, least one."))

                    if sale_job_id is None:
                        sale_job_id = sale_job_order.create({
                            'sale_order_id': self.id,
                            'is_repair': is_repair
                        })
                    if line.package_id.process_ids:
                        if line.left_front:
                            job_left_front =  self._get_default_job(order, line, sale_job_id.id)
                            job_left_front.update({
                                    'wheels_perticulars' : 'Left Front',
                                    'barcode_no' : line.left_front_barcode,
                                })
                            job_id = sb_job_order.create(job_left_front)
                            for process in line.package_id.process_ids:
                                job_left_front_line = self._get_default_job_line(order, line)
                                self._get_job_line(process, job_left_front_line)
                                job_left_front_line.update({
                                    'wheels_perticulars': 'Left Front',
                                    'barcode_no': line.left_front_barcode,
                                    'job_order_id': job_id.id,
                                    'main_process': process.main_process, 
                                    })
                                sb_job_item.create(job_left_front_line)

                        if line.right_front:
                            job_right_front =  self._get_default_job(order, line, sale_job_id.id)
                            job_right_front.update({
                                     'wheels_perticulars' : 'Rigt Front',
                                     'barcode_no' : line.right_front_barcode,
                                })
                            job_right_id = sb_job_order.create(job_right_front)
                            for process in line.package_id.process_ids:
                                job_right_front_line = self._get_default_job_line(order, line)
                                self._get_job_line(process, job_right_front_line)
                                job_right_front_line.update({
                                    'wheels_perticulars': 'Rigt Front',
                                    'barcode_no': line.right_front_barcode,
                                    'job_order_id': job_right_id.id,
                                    'main_process': process.main_process, 
                                    })
                                sb_job_item.create(job_right_front_line)
                        if line.left_back:
                            job_left_back =  self._get_default_job(order, line, sale_job_id.id)
                            job_left_back.update({
                                     'wheels_perticulars' : 'Left Back',
                                     'barcode_no' : line.right_front_barcode,
                                })
                            job_right_id = sb_job_order.create(job_left_back)
                            for process in line.package_id.process_ids:
                                job_left_back_line = self._get_default_job_line(order, line)
                                self._get_job_line(process, job_left_back_line)
                                job_left_back_line.update({
                                    'wheels_perticulars': 'Left Back',
                                    'barcode_no': line.left_back_barcode,
                                    'job_order_id': job_right_id.id,
                                    'main_process': process.main_process, 
                                    })
                                sb_job_item.create(job_left_back_line)

                        if line.right_back:
                            job_right_back =  self._get_default_job(order, line, sale_job_id.id)
                            job_right_back.update({
                                     'wheels_perticulars' : 'Right Back',
                                     'barcode_no' : line.right_back_barcode,
                                })
                            job_right_id = sb_job_order.create(job_right_back)
                            for process in line.package_id.process_ids:
                                job_right_back_line = self._get_default_job_line(order, line)
                                self._get_job_line(process, job_right_back_line)
                                job_right_back_line.update({
                                    'wheels_perticulars': 'Right Back',
                                    'barcode_no': line.right_back_barcode,
                                    'job_order_id': job_right_id.id,
                                    'main_process': process.main_process, 
                                    })
                                sb_job_item.create(job_right_back_line)
                        if line.spare_wheel:
                            job_wheels_perticulars =  self._get_default_job(order, line, sale_job_id.id)
                            job_wheels_perticulars.update({
                                     'wheels_perticulars' : 'Spare Wheel',
                                     'barcode_no' : line.spare_wheel_barcode,
                                })
                            job_right_id = sb_job_order.create(job_wheels_perticulars)
                            for process in line.package_id.process_ids:
                                job_wheels_perticulars_line = self._get_default_job_line(order, line)
                                self._get_job_line(process, job_wheels_perticulars_line)
                                job_wheels_perticulars_line.update({
                                    'wheels_perticulars': 'Spare Wheel',
                                    'barcode_no': line.spare_wheel_barcode,
                                    'job_order_id': job_right_id.id,
                                    'main_process': process.main_process, 
                                    })
                                sb_job_item.create(job_wheels_perticulars_line)

        return res

    def getparseddata(self, xmldata):
        from . import xmltodict
        import json
        o = xmltodict.parse(xmldata.replace("\n",'').replace("  ",''))
        return json.loads(json.dumps(o))

        o = xmltodict.parse(xmldata.replace("\n",'').replace("  ",''))
        return json.loads(json.dumps(o))

    @api.multi
    @api.onchange('vehicle_reg')
    def onchange_vehicle_reg(self):
        res = {}
        if self.vehicle_reg:
            _brand = self.env['sb.brands']
            _model = self.env['sb.vehicle.model']
            try:
                r  = requests.get('http://www.hpixml.com/servlet/HpiGate1_0?efxid=0437730&password=bear&initials=xx&function=SEARCH&vrm=%s&XML=YES&product=HPI11&devicetype=XM'% self.vehicle_reg.replace(" ", ""))

                dvla_data = self.getparseddata(r.content.replace('<?xml version="1.0"?>', ''))

                basic = dvla_data.get('HPICheck_Query').get('Basic', {})
                Additional = dvla_data.get('HPICheck_Query').get('Additional', {})
                if basic.get('Make', False):

                    wheels_make = basic.get('Make')
                    wheels_model = basic.get('Model')

                    wheel_code = Additional.get('Wheelplan_code')
                    color =  basic.get('Colour')
                    model_code =  basic.get('Model_Code')
                    transmission =  basic.get('Transmission')
                    model_ids = _model.search([('name', '=', wheels_model)])

                    if not model_ids:
                        brand_ids = _brand.search([('name', '=', wheels_make)])
                        if not brand_ids:
                            create_brand = _brand.create({'name' : wheels_make})
                            res['make_id'] = create_brand
                        else:
                            res['make_id'] =  brand_ids.id
                        create_model = _model.create({
                                'name' : wheels_model,
                                'brand_id' : brand_ids.id if brand_ids else create_brand,
                                'make_year': Additional.get('Mfr_Year'),
                                'wheels_code': Additional.get('Wheelplan_code'),
                                'wheels': Additional.get('Wheelplan'), 
                                'color':  color, 
                                'fuel_type': basic.get('fuel'), 
                                'transmission_type':  basic.get('Transmission'),
                                'number': self.vehicle_reg,
                            })
                        res['model_id'] = create_model
                    else:
                        res['make_id'] = model_ids.brand_id.id 
                        res['model_id'] = model_ids.id
            except Exception as e:
                pass
            self.update(res)

 #TODO need to double check this method, in XML its not removed............................................
    @api.multi
    @api.onchange()
    def onchange_set(self):
        res = {}
        if self.set:
            res['left_front'] = True
            res['left_back']  = True
            res['right_front'] = True
            res['right_back']  = True
        return {'value': res}
    
    @api.multi
    @api.onchange()
    def onchange_make_id(self):
        res = {}

        return {'value': res, 'domain': {'model_id': [('brand_id','=',self.make_id)]}}

    @api.multi
    @api.onchange()
    def onchange_model_id(self):
        res = {}

        return {'value': res, 'domain': {'size_id': [('model_id','=',self.model_id)],'style_id': [('model_id','=',self.model_id)],'type_id': [('model_id','=',self.model_id)]}}
    
