import logging
import requests
import json
from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.osv import osv

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    vehicle_reg = fields.Char(string = 'Vehicle Registration')
    make_id = fields.Many2one('sb.brands', string = 'Make')
    model_id = fields.Many2one('sb.vehicle.model', string ='Model')
    
    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'sb_wheels.report_invoice_fa')
    
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

    
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    
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
    product_image = fields.Binary('Image')
    default_code = fields.Char(string = 'Reference Number')


    @api.onchange('left_front','right_front','left_back','right_back','spare_wheel', 'quantity')
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
                self.quantity = qty

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
    def _onchange_product_id(self):
        result = super(account_invoice_line, self)._onchange_product_id()
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
            vals['quantity'] = total_qty or self.quantity

        self.update(vals)
        return result