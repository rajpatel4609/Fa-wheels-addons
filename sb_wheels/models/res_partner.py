from openerp import api, fields, models, _
import requests
import json
import psycopg2
from openerp.exceptions import UserError

class res_partner(models.Model):
    _inherit = "res.partner"

    postcode = fields.Char(string = 'Postcode')
    house_number = fields.Char(string = 'House Number')
    county = fields.Char(string = 'County')
    customer_type = fields.Selection([('b2c','Retail'),('b2b','Trade')], string = 'Type', default ='b2c', required=False)
    classification = fields.Selection([('tier1','Tier 1'),('tier2','Tier 2'),('tier3','Tier 3'),], string = 'Classification', required=False)

    @api.onchange('postcode')
    def onchange_postcode(self):
        row = None
        try:
            if not self.postcode: return
            connection = (psycopg2.connect("dbname='postcode' user='ubuntu' host='50.112.178.23' password='admin123'"))
            cr = connection.cursor()
            cr.execute("SELECT postcode1,street,town,county from POSTCODE where postcode='%s'" % (self.postcode))
            row = cr.fetchone()

        except Exception as e:
            print "ddddddd",e
            pass
        if row:
            self.zip= row[0]
            self.street = row[1].title() if row[1] else None
            self.state_id = self.env['res.country.state'].search([('name', '=', row[3])]).id
            self.city = row[2].title() if row[2] else None
        else :
            raise UserError(_('There is no data found for Postcode: %s Enter valid postcode') % (self.postcode))