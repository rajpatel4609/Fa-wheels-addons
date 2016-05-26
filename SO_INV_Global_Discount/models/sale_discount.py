from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'dicount_type')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.dicount_type == 'fix':
                s_price = line.price_unit * line.product_uom_qty
                price = s_price - line.discount
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1, product=line.product_id, partner=line.order_id.partner_id)
            else :
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    discount = fields.Float(string='Discount', digits=dp.get_precision('Discount'), default=0.0)
    dicount_type = fields.Selection([('fix','Fix Amount'), ('percentage','Percentage(%)')], string='Discount Method', default='percentage', readonly=True, states={'draft': [('readonly', False)]}, help="Select Appropriate Discount method on Sale order")
    
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update ({'dicount_type': self.dicount_type})
        return res

    
    
 
 
 
    