from openerp import api, fields, models, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import copy

class product_product(models.Model):
    _inherit = "product.product"

    donor_wheels = fields.Boolean('Donor Wheels')
    exchange_stock = fields.Boolean('Exchange Stock', help="Allow to exchange this wheel, Exchange process will be afffected to sales line.")
    service = fields.Boolean('Direct Sales', help="Allow to direct sale for ths wheel, No exchange of product require, direct sales.")
    
    make_id = fields.Many2one('sb.brands', string = 'Make')
    model_id = fields.Many2one('sb.vehicle.model', string = 'Model')
    size_id = fields.Many2one('sb.model.size', string = 'Wheel Size')
    style_id = fields.Many2one('sb.model.style', string = 'Wheel Style')
    type_id = fields.Many2one('sb.model.type', string = 'Model Type')
    value = fields.Selection([('high_value','High Value'),('low_value','Low Value')], string = 'Value', required=False)
    profit = fields.Selection([('high_profit','High Profit'),('low_profit','Low Profit')], string = 'Profit', required=False)
    availability = fields.Selection([('normal','Normal'),('rare','Rare')], string ='Availability', required=False)
    process = fields.Selection([('unit','Unit'),('pair','Pair'),('set','Set')], 'Process', required=False)
    move = fields.Selection([('normal','Normal'),('fast_moving','Fast Moving'),('slow_moving','Slow Moving')], string = 'Move', required=False)
    sb_type = fields.Selection([('wheel','Wheel'),('tyre','Tyre'),('accessories','Accessories'),('services','Services')], string ='Type', required=False)
    product_sale_type = fields.Selection([('sale','Sale'),('exchange','Exchange'), ], string = 'Product Sale Type', required=False)
    service_sale_type = fields.Selection([('refurbish','Refurbish'),('repair','Repair Service'), ('other_service','Other Services')], string ='Service Type', required=False)
    
    
    # FAWHEELS PRODUCTS PRICESING
    sale_front_1unit = fields.Float(string = 'Sales Front 1 Unite', help="Sale Price Front")
    sale_back_1unit = fields.Float(string = 'Sales Back 1 Unite', help="Sale Price Back")
    sale_front_pair = fields.Float(string = 'Sales Front Pair')
    sale_back_pair = fields.Float(string = 'Sales Back Pair')
    sale_front_set4 = fields.Float(string = 'Sales Front 4 Set ')
    sale_front_set5 = fields.Float(string = 'Sales Front 5 Set')


    exchange_front_1unit = fields.Float(string = 'Exchange Front 1 Unite', help="Sale Price Front")
    exchange_back_1unit = fields.Float(string ='Exchange Back 1 Unite', help="Sale Price Back")
    exchange_front_pair = fields.Float(string = 'Exchange Front Pair')
    exchange_back_pair = fields.Float(string = 'Exchange Back Pair')
    exchange_front_set4 = fields.Float(string = 'Exchange Front 4 Set ')
    exchange_front_set5 = fields.Float(string = 'Exchange Front 5 Set')

    wheel_width = fields.Many2one('sb.wheels.width', string ='Width')
    wheel_height = fields.Many2one('sb.wheels.height', string ='Height')
    wheel_speed = fields.Many2one('sb.wheels.speed', string ='Speed')
    wheel_diameter = fields.Many2one('sb.wheels.diameter', string ='Diameter')
    wheel_offset = fields.Many2one('sb.wheels.offset', string ='Offset')
    wheel_pcd = fields.Many2one('sb.wheels.pcd', string='PCD')
    wheel_color = fields.Many2one('sb.wheels.color', string ='Color')
    wheel_finish = fields.Boolean(string = 'Finished Available')
    
    #Services
    package_id = fields.Many2one('sb.product.package', string ='Package')
    #tyre
    sale_tyre_front_1unit = fields.Float(string = 'Sales Front 1 Unite(Tyre)', help="Sale Price Front")
    sale_tyre_back_1unit = fields.Float(string = 'Sales Back 1 Unite(Tyre)', help="Sale Price Back")
    sale_tyre_front_pair = fields.Float(string = 'Sales Front Pair(Tyre)')
    sale_tyre_back_pair = fields.Float(string = 'Sales Back Pair(Tyre)')
    sale_tyre_front_set4 = fields.Float(string = 'Sales Front 4 Set(Tyre)')
    sale_tyre_front_set5 = fields.Float(string = 'Sales Front 5 Set(Tyre)')
    parent_id  =  fields.Many2one('product.product','Parent Product', select=True, ondelete='cascade')
    sub_product_line = fields.One2many('product.product', 'parent_id', string='Sub Products', copy=True)
    sub_product_type = fields.Selection([('front','Front'),('back','Back'),('spare_wheels','Spare Wheels')], string = 'Sub Product Types', required=False)
    is_sub_product = fields.Boolean("Is Sub Product", default=False, readonly=True)
    has_sub_product = fields.Boolean("Has Sub Product", default=False, readonly=True)
    wheel_model = fields.Char("Wheel Model")
    unfinish_stock = fields.Integer(string='Unfinished Stock', readonly=True)
    is_unfinish = fields.Boolean(string = 'Is Unfinished', help ='Mark this box for Unfinished products')
 
    
    @api.multi
    def unfinished_product(self):
        return True
 
    @api.v7
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if type(ids) == int:
            ids = [ids]
        res = []
        if not ids:
            return res
        services = self.read(cr, uid, ids, ['name', 'default_code'], context=context)
        for service in services:
            if service and service['default_code']: 
                title = "%s [%s]" % (service['name'], service['default_code'])
            else:
                title = service['name']
            res.append((service['id'], title))
        return res

    @api.v8
    @api.depends('name', 'default_code')
    def name_get(self):
        res = []
        for service in self:
            title = service['name']
            if service and service['default_code']: 
                title = "%s [%s]" % (title, service['default_code'])
            res.append((service['id'], title))  
        return res
    
    @api.onchange('sb_type')
    def onchange_sb_type(self):
        if not self.default_code and self.sb_type:
            self.default_code = "%s%s"%(self.sb_type[0].upper(), self.env['ir.sequence'].get("sb.product.product") or '/')

    @api.multi
    def sub_product(self):
        sub_product = []
        if self.sb_type in ['wheel', 'tyre'] and not self.has_sub_product:
            for xx in ["front", "back", "spare_wheels"]:
                sub_product.append(self.with_context({'return':True}).copy(default={
                    'is_sub_product': True,
                    'sub_product_type': xx,
                    }))
            for product in sub_product:
                product.write({
                    'parent_id' : self.id,
                    })
            self.write({'has_sub_product': True})

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if  context.get('return'):
            vals['name']  = vals['name'].replace("(copy)", "/" + vals.get('sub_product_type'))

        return super(product_product, self).create(cr, uid, vals, context=context)
