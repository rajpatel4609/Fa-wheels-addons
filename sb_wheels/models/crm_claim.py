from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError



class crm_lead(models.Model):
    _inherit = "crm.lead"
    source_of_lead = fields.Selection([
                    ('you_contacted_me', 'You Contacted Me!'),
                    ('search_engine','Search Engine'),
                    ('social_network','Social Network'),
                    ('advertisement','Advertisement'),
                    ('friend','Friend'),
                    ('event','Event'),
                    ('forum_or_blog','Forum or Blog'),
                    ('other','Other'),
                    ], 'Source of lead')

class crm_claim(models.Model):
    _inherit = "crm.claim"

    return_items_ids = fields.One2many('return.items', 'claim_id', string = 'Return Items')
    
    #First Set RElated locations on Company
    #On given location, this method change status of lines to restock
    # and create stock move, from cust location to stock location or Scrap Location
    def btn_return_items(self):
        _return_items =  self.env['return.items']
        if not self.return_items_ids:
            raise UserError(_("Return items should be require their.") )
        
        if not self.company_id.default_scrap_location_id:
            raise UserError(_("In Company setup default scrap location. Open your company form and setup this."))

        if not  self.company_id.default_stock_location_id:
            raise UserError(_("In Company setup default stock location. Open your company form and setup this."))

        if not  self.company_id.default_cust_location_id:
            raise UserError(_("In Company setup default customer location. Open your company form and setup this."))

        for line in self.return_items_ids:
            if line.status != 'a':
                continue
            data = { 'invoice_state': 'none',
                     'name': "Return %s %s" %(line.product_id.name , line.reason),
                     'product_id': line.product_id.id,
                     'date_expected': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'product_uom_qty': float(line.quantity),
                     'wheel_type': line.wheel_type,
                     'product_uom': line.product_id.uom_id.id,
                    }
            
            data['location_id'] = self.company_id.default_cust_location_id.id
            data['location_dest_id'] = self.company_id.default_stock_location_id.id  if line.return_kind == 'normal' else  self.company_id.default_scrap_location_id.id
            _return_items.write([line.id], {'status': 'b'})
            mv_id = self.env['stock.move'].create(data)
            self.env['stock.move'].action_done([mv_id])
            
        return True

class return_items(models.Model):
    _name = "return.items"
    _description = "return.items"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string = 'Product', required=True)
    wheel_type = fields.Selection([('front','Front'),('rear','Rear'),('set4','Set 4'),('set5','Set 5')], 'Wheel Type', required=False, help="Front, Rear, Set of 4 (2 Front& 2 Rear), Set of 5 (all the wheel, front/rear  3 front, 2 rear)")
    quantity =  fields.Integer('Quantity', required=True)
    reason = fields.Char('Reason', required=False)
    datetime = fields.Datetime('Date', required=True, default = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return_kind = fields.Selection([('a','Normal'), ('b','Damaged')], string ='Behavior', required=True)
    user_id = fields.Many2one('res.users', string = 'User', required=True, default=lambda self: self.env.user)
    claim_id = fields.Many2one('crm.claim', string = 'Claim', required=False) 
    status = fields.Selection([('a','Draft'),('b','ReStocked')], 'Status', required=False, default='a')
    

class view(models.Model):
    _inherit = 'ir.ui.view'
    _name = 'ir.ui.view'
    type = fields.Selection([
            ('tree','Tree'),
            ('form','Form'),
            ('graph', 'Graph'),
            ('pivot', 'Pivot'),
            ('calendar', 'Calendar'),
            ('diagram','Diagram'),
            ('gantt', 'Gantt'),
            ('kanban', 'Kanban'),
            ('sales_team_dashboard', 'Sales Team Dashboard'),
            ('search','Search'),
            ('qweb', 'QWeb'),
            ('fb_team_dashboard', 'FA Sale Team')], string='View Type')





