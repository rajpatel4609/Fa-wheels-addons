from openerp import api, fields, models, _

class res_company(models.Model):
    _inherit = "res.company"

    default_scrap_location_id = fields.Many2one('stock.location', string ='Default Scrap Location')
    default_stock_location_id = fields.Many2one('stock.location', string = 'Default Stock Location')
    default_cust_location_id = fields.Many2one('stock.location', string = 'Default Customer Location')
    term_and_condition = fields.Text('Term & Condtition')
    bank_ids = fields.One2many('res.partner.bank','company_id', string = 'Bank Accounts ')


