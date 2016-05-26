from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def get_taxes_values(self):
        taxes = []
        tax_grouped = {}
        for line in self.invoice_line_ids:
            if not line.dicount_type:
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if line.invoice_line_tax_ids:
                    taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            elif line.dicount_type == 'fix':
                s_price = line.price_unit * line.quantity
                price = s_price - line.discount
                if line.invoice_line_tax_ids:
                    taxes += line.invoice_line_tax_ids.compute_all(price, line.invoice_id.currency_id, 1, product=line.product_id, partner=line.invoice_id.partner_id)['taxes']
            elif line.dicount_type == 'percentage':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if line.invoice_line_tax_ids:
                    taxes += line.invoice_line_tax_ids.compute_all(price, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
        for tax in taxes:
            val = {
                'invoice_id': self.id,
                'name': tax['name'],
                'tax_id': tax['id'],
                'amount': tax['amount'],
                'manual': False,
                'sequence': tax['sequence'],
                'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
            }

            # If the taxes generate moves on the same financial account as the invoice line,
            # propagate the analytic account from the invoice line to the tax line.
            # This is necessary in situations were (part of) the taxes cannot be reclaimed,
            # to ensure the tax move is allocated to the proper analytic account.
            if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                val['account_analytic_id'] = line.account_analytic_id.id

            key = tax['id']
            if key not in tax_grouped:
                tax_grouped[key] = val
            else:
                tax_grouped[key]['amount'] += val['amount']
        return tax_grouped

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
        
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id','dicount_type')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if not self.dicount_type:
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        elif self.dicount_type == 'fix':
            s_price = self.price_unit * self.quantity
            price = s_price - self.discount
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, self.invoice_id.currency_id, 1, product=self.product_id, partner=self.invoice_id.partner_id)
        elif self.dicount_type == 'percentage':
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, self.invoice_id.currency_id, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
            price = price * self.quantity
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else price
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        
    dicount_type = fields.Selection([('fix','Fix Amount'), ('percentage','Percentage(%)')], string='Discount Type', default='percentage',  help="Select Appropriate Discount method on Sale order")
    price_subtotal = fields.Monetary(string='Amount',
        store=True, readonly=True, compute='_compute_price')
    price_subtotal_signed = fields.Monetary(string='Amount Signed', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_price',
        help="Total amount in the currency of the company, negative for credit notes.")