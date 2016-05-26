from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

class sb_job_item(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "sb.job.item"
    _description = "sb.job.item"
    _order = "sequence"

    name = fields.Char(string = 'Name')
    not_include =  fields.Boolean(string = "Not Include In Workflow")
    subprocess_id = fields.Many2one('sb.subprocess', string = 'Sub Process')
    tag_ids = fields.Many2many('sb.process.tag', 'rel_process_item_tag', 'newid_one', 'currentmodel_id', string = 'Tags')
    tag_title = fields.Char(string ='Tags')
    main_process = fields.Selection([('p1', 'Tyre Removal'),('p2', 'Strip Old Coating'),
                                      ('p3', 'Sand Blasting'),('p4', 'Prep & Repair Team'),
                                      ('p5', 'Ceremic Polishing'),('p6', 'Paint'),
                                      ('p7', 'Diamond Cut'),('p8', 'Lacquer'),
                                      ('p9', 'Quality Check'),('p10', 'Finished Goods'),
                                      ('p11', 'Tyre Fitting')
                                      ], string = 'Stage', required=True)
    job_order_id = fields.Many2one('sb.job.order', string = 'Job Order')
    product_package_id = fields.Many2one('sb.product.package', string = 'Package')
    barcode_no = fields.Char(string = 'Wheel Code',readonly=False)
    wheels_perticulars = fields.Char(string = 'Wheels Perticulars')
    is_completed =  fields.Boolean(string = 'Is Completed')
    sequence = fields.Integer(string = 'Sequence')
    comment = fields.Char(string ='Comments')
    
    vehicle_reg =  fields.Char(string = 'Vehicle Registration')
    make_id = fields.Many2one('sb.brands', string = 'Make')
    model_id = fields.Many2one('sb.vehicle.model', string = 'Model')
    size_id = fields.Many2one('sb.model.size', string = 'Wheel Size')
    style_id = fields.Many2one('sb.model.style', string = 'Wheel Style')
    
    customer_id = fields.Many2one('res.partner', string = 'Customer')
    sale_order_id = fields.Many2one('sale.order', string = 'Sale Order')
    collection_date = fields.Datetime('sale.order', related='sale_order_id.collection_date')
    booking_date = fields.Datetime('sale.order', related='sale_order_id.booking_date')
    only_refurb_order_id = fields.Many2one('sb.product.finish', string ='Refurbish', readonly=True)
    color = fields.Integer(string='Color')

    @api.multi
    def return_action_to_open(self):
        if self._context.get("object") == 'sb_job_order':
            res = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sb_job_order_action')
            res['domain'] = [('id', '=', self.job_order_id.id)]
        elif self._context.get("object") == 'res_partner':
            res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_partner_form')
            res['domain'] = [('id', '=', self.customer_id.id)]
        elif self._context.get("object") == 'sale_order':
            res = self.env['ir.actions.act_window'].for_xml_id('sale', 'action_orders')
            res['domain'] = [('id', '=', self.sale_order_id.id)]
        return res

    def restock_product(self, ex):
        data =  {
         'name': "Refurbish Item %s %s" %(ex.to_product.name , ex.name or ''),
         'product_id': ex.to_product.id,
         'date_expected': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         'product_uom_qty': 1,
         'product_uom': ex.to_product.uom_id.id,
         'location_id': ex.company_id.default_cust_location_id.id,
         'location_dest_id': ex.company_id.default_stock_location_id.id
        }
        stock_job = self.env['stock.move']
        stock_id = stock_job.create(data)
        stock_id.action_done()

    @api.multi
    def mark_as_done(self):
        for res in self:
            domian = [('sequence', '<', self.sequence), 
                      ('is_completed','=', False),
                      ('job_order_id','=', self.job_order_id.id)
                      ]
            if len(self.search(domian)):
                raise UserError(_("Please complete Job Item in Sequence.") )
            res.is_completed = True
            if res.only_refurb_order_id.id and res.main_process == 'p9':
                self.restock_product(res.only_refurb_order_id)
                unfinish = self.only_refurb_order_id.from_product
                unfinish.write({'unfinish_stock': unfinish.unfinish_stock - 1})

class sb_job_order(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "sb.job.order"
    _description = "sb.job.order"
    _order = "collection_date desc, date desc"

    @api.multi
    def _model_booking_ready_get_fnc(self):
        sb_job_item = self.env['sb.job.item']
        for res in self:
            is_done = sb_job_item.search_count([('is_completed', '=', 'True'), ('job_order_id', '=', res.id)])
            total = sb_job_item.search_count([('job_order_id', '=', res.id), ('not_include', '=', False)])
            if is_done >= total:
                res.booking_ready = True
            else:
                res.booking_ready = False
    
    name = fields.Char(string = 'Job Order',readonly=True)
    date = fields.Datetime(string = 'Date', readonly=True, default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    booking_date = fields.Datetime(string = 'Booking Date', readonly=False)
    collection_date = fields.Datetime(string = 'Collection Date', readonly=False)
    end_date = fields.Datetime(string = 'Completed Date', readonly=True)
    
    product_id = fields.Many2one('product.product', string = 'Wheel')
    barcode_no = fields.Char(string = 'Wheel Code',readonly=False)
    customer_id = fields.Many2one('res.partner', string = 'Customer')
    sale_order_id = fields.Many2one('sale.order', string ='Sale Order')
    sale_order_line_id = fields.Many2one('sale.order.line', string = 'Sale Service Item')
    only_refurb_order_id = fields.Many2one('sb.product.finish', string = 'Only Refurbish', readonly=True)
    product_package_id = fields.Many2one('sb.product.package', string = 'Package')
    process_ids = fields.One2many('sb.job.item','job_order_id', string = 'Processes', required=False)
    
    wheels_perticulars = fields.Char(string = 'Wheels Perticulars')
    vehicle_reg = fields.Char(string = 'Vehicle Registration')
    make_id = fields.Many2one('sb.brands', string = 'Make')
    model_id = fields.Many2one('sb.vehicle.model', string = 'Model')
    size_id = fields.Many2one('sb.model.size', string = 'Wheel Size')
    style_id = fields.Many2one('sb.model.style', string = 'Wheel Style')
    main_job_id = fields.Many2one('sale.job.order', string = 'Main job', required=True, readonly=True)
    is_exchange = fields.Boolean('Is Exchange', default = False)
    is_repair = fields.Boolean('Is Repair', default = False)
    booking_ready = fields.Boolean(compute = '_model_booking_ready_get_fnc', string='Ready', default = False)

    state =  fields.Selection([('p1', 'Tyre Removal'),('p2', 'Strip Old Coating'),
                                      ('p3', 'Sand Blasting'),('p4', 'Prep & Repair Team'),
                                      ('p5', 'Ceremic Polishing'),('p6', 'Paint'),
                                      ('p7', 'Diamond Cut'),('p8', 'Lacquer'),
                                      ('p9', 'Quality Check'),('p10', 'Finished Goods'),
                                      ('p11', 'Tyre Fitting')
                                      ], string = 'Current Stage', required=False)
    only_refurb_order_id = fields.Many2one('sb.product.finish', string = 'Refurbish', readonly=True)

   #FROM VIEWS SIDE NOT CALL ANYWHERE 
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('JBO')
        return super(sb_job_order, self).create(vals)


class sale_job_order(models.Model):
    _name = "sale.job.order"
    _description = "Connecting Job order and sale order"
    
    @api.multi
    def _methods_job_completed(self):
        for res in self:
            count = 0
            for job in res.job_ids:
                if job.booking_ready:
                    count = count + 1
            res.job_completed =  count

    @api.multi
    def _methods_job_item_completed(self):
        sb_job_item = self.env['sb.job.item']
        for res in self:
            res.job_item_completed = sb_job_item.search_count([("sale_order_id", "=", res.sale_order_id.id), ("is_completed", "=", True)])

    @api.multi
    def _total_job_item(self):
        sb_job_item = self.env['sb.job.item']
        for res in self:
            res.total_job_item = sb_job_item.search_count([("sale_order_id", "=", res.sale_order_id.id)])

    @api.multi
    def _total_job(self):
        sb_job_item = self.env['sb.job.order']
        for res in self:
            res.total_job = sb_job_item.search_count([("sale_order_id", "=", res.sale_order_id.id)])

    def _get_state(self):
        return self.env['ir.model.data'].xmlid_to_res_id('sb_wheels.sale_job_order_state_1')

    @api.depends('state')
    @api.multi
    def _get_state_name(self):
        for x in self:
            x.domain_name = x.state.name
    
    @api.multi
    def mark_as_inprogress(self):
        for rec in self:
            rec.state = self.env['ir.model.data'].xmlid_to_res_id('sb_wheels.sale_job_order_state_2')

    @api.multi
    def mark_as_ready(self):
        if self.job_completed == self.total_job:
            for rec in self:
                rec.state = self.env['ir.model.data'].xmlid_to_res_id('sb_wheels.sale_job_order_state_3')
        else:
            raise UserError(_('Only  %s job items complated from %s, Complate all job items before proceed next stage') % (self.job_completed, self.total_job))
    
    @api.multi
    def mark_as_done_job(self):
        sb_job_order = self.env['sb.job.order']
        for rec in self:
            rec.state = self.env['ir.model.data'].xmlid_to_res_id('sb_wheels.sale_job_order_state_4')

    @api.multi
    def mark_as_cancel(self):
        for rec in self:
            rec.state = self.env['ir.model.data'].xmlid_to_res_id('sb_wheels.sale_job_order_state_5')
    

    state = fields.Many2one('sale.job.order.state', string = 'State', default=lambda self: self._get_state() , required=True, readonly=True)
    sale_order_id = fields.Many2one('sale.order', string = 'Sale Order', required=True, readonly=True)
    job_ids = fields.One2many('sb.job.order', 'main_job_id', string='Refurbish Process', copy=True)
    color = fields.Integer(string='Color')
    total_job = fields.Integer(string="All Job", compute='_total_job')
    job_completed = fields.Integer(string="Job Completed", compute='_methods_job_completed')
    job_item_completed = fields.Integer(string= "Job Item Completed", compute='_methods_job_item_completed')
    total_job_item = fields.Integer(string = "All Job Item", compute='_total_job_item')
    collection_date = fields.Datetime('sale.order', related='sale_order_id.collection_date')
    booking_date = fields.Datetime('sale.order', related='sale_order_id.booking_date')
    domain_name = fields.Char(compute="_get_state_name", store=True)
    is_exchange = fields.Boolean('Is Exchange', default = False)
    is_repair = fields.Boolean('Is Repair', default = False)
    
    @api.multi
    def return_action_to_open(self):
        
        if self._context.get("object") == 'sb_job_calendar':
            res = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sb_job_order_action_booking_calender')
            res['domain'] = [('id', '=', self.sale_order_id.id)]
        elif self._context.get("object") == 'sb_job_order':
            res = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sb_job_order_action')
            res['domain'] = [('sale_order_id', '=', self.sale_order_id.id)]
        elif self._context.get("object") == 'sb_job_item':
            res = self.env['ir.actions.act_window'].for_xml_id('sb_wheels', 'sb_job_item_step_action_sale_job_order')
            res['domain'] = [('sale_order_id', '=', self.sale_order_id.id), ('is_completed', '!=', True)]
        elif self._context.get("object") == 'sale_order':
            res = self.env['ir.actions.act_window'].for_xml_id('sale', 'action_orders')
            res['domain'] = [('id', '=', self.sale_order_id.id)]
        return res

class sale_job_order_state(models.Model):
    _name = "sale.job.order.state"
    _description = "Connecting Job order and sale order"

    name = fields.Char(string = 'Job state Name')
    sequence = fields.Integer(string = 'Sequence')
    fold = fields.Boolean(string = 'Folded in Tasks Pipeline')