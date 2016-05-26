from openerp import tools
from openerp import api, fields, models, _

class stock_move(models.Model):
    _inherit = "stock.move"

    serialcode = fields.Char(string = 'Serial Code', help='Serial Number Assign when Item move from stock to customer')

class procurement_order(models.Model):
    _inherit = "procurement.order"

    wheel_type = fields.Selection([('front','Front'),('rear','Rear'),('set4','Set 4'),('set5','Set 5')], string = 'Wheel Type', required=False, help="Front, Rear, Set of 4 (2 Front& 2 Rear), Set of 5 (all the wheel, front/rear  3 front, 2 rear)")
    
    @api.model
    def _run_move_create(self, procurement):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'move') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        vals =  super(procurement_order, self)._run_move_create(procurement)
        vals['wheel_type'] = procurement.wheel_type
        return vals



class stock_change_product_qty(models.TransientModel):
    
    _inherit = "stock.change.product.qty"

    wheel_type = fields.Selection([('front','Front'),('rear','Rear'),('set4','Set 4'),('set5','Set 5')], string = 'Wheel Type', required=False, help="Front, Rear, Set of 4 (2 Front& 2 Rear), Set of 5 (all the wheel, front/rear  3 front, 2 rear)")

    _rec_name = 'product_id'

    def change_product_qty(self, cr, uid, ids, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_line_obj = self.pool.get('stock.inventory.line')

        for data in self.browse(cr, uid, ids, context=context):
            if data.new_quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))
            ctx = context.copy()
            ctx['location'] = data.location_id.id
            ctx['lot_id'] = data.lot_id.id
            inventory_id = inventory_obj.create(cr, uid, {
                'name': _('INV: %s') % tools.ustr(data.product_id.name),
                'product_id': data.product_id.id,
                'location_id': data.location_id.id,
                'lot_id': data.lot_id.id}, context=context)
            product = data.product_id.with_context(location=data.location_id.id)
            th_qty = product.qty_available
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': data.new_quantity,
                'location_id': data.location_id.id,
                'product_id': data.product_id.id,
                'product_uom_id': data.product_id.uom_id.id,
                'theoretical_qty': th_qty,
                'prod_lot_id': data.lot_id.id,
                'wheel_type': data.wheel_type,
            }
            inventory_line_obj.create(cr , uid, line_data, context=context)
            inventory_obj.action_done(cr, uid, [inventory_id], context=context)
        return {}

class stock_inventory_line(models.Model):
    _inherit = "stock.inventory.line"

    wheel_type = fields.Selection([('front','Front'),('rear','Rear'),('set4','Set 4'),('set5','Set 5')], string = 'Wheel Type', required=False, help="Front, Rear, Set of 4 (2 Front& 2 Rear), Set of 5 (all the wheel, front/rear  3 front, 2 rear)")

    def _resolve_inventory_line(self, cr, uid, inventory_line, context=None):
        stock_move_obj = self.pool.get('stock.move')
        diff = inventory_line.theoretical_qty - inventory_line.product_qty
        if not diff:
            return
        #each theorical_lines where difference between theoretical and checked quantities is not 0 is a line for which we need to create a stock move
        vals = {
            'name': _('INV:') + (inventory_line.inventory_id.name or ''),
            'product_id': inventory_line.product_id.id,
            'product_uom': inventory_line.product_uom_id.id,
            'date': inventory_line.inventory_id.date,
            'company_id': inventory_line.inventory_id.company_id.id,
            'inventory_id': inventory_line.inventory_id.id,
            'state': 'confirmed',
            'restrict_lot_id': inventory_line.prod_lot_id.id,
            'restrict_partner_id': inventory_line.partner_id.id,
         }
        inventory_location_id = inventory_line.product_id.property_stock_inventory.id
        if diff < 0:
            #found more than expected
            vals['location_id'] = inventory_location_id
            vals['location_dest_id'] = inventory_line.location_id.id
            vals['product_uom_qty'] = -diff
        else:
            #found less than expected
            vals['location_id'] = inventory_line.location_id.id
            vals['location_dest_id'] = inventory_location_id
            vals['product_uom_qty'] = diff
        vals['wheel_type'] = inventory_line.wheel_type
        return stock_move_obj.create(cr, uid, vals, context=context)

