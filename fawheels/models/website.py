# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.http import request


class website_reviews(models.Model):
    _name = 'website.customer.comment'

    customer_name = fields.Char(string='Customer Name')
    customer_image = fields.Binary(string='Customer Image')
    customer_comment = fields.Text(string="Customer comment")


class website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_brand_img(self):
        brands = self.env['sb.brands'].sudo().search([])
        return brands

    @api.multi
    def get_country_list(self):
        countries = self.env['res.country'].sudo().search([])
        return countries

    @api.multi
    def shop_features_alloy(self):
        products = self.env['product.template'].sudo().search([('website_published', '=', True), ('is_features', '=', True)], limit=6)
        return products

    @api.multi
    def shop_arrivals_alloy(self):
        products = self.env['product.template'].sudo().search([('website_published', '=', True), ('is_arrival', '=', True)], limit=6)
        return products

    @api.multi
    def quote_sb_brands(self):
        sb_brands = self.env["sb.brands"].sudo().search([])
        return sb_brands

    @api.multi
    def quote_wheel_size(self):
        product_wheel_size = self.env['sb.model.size'].sudo().search([], order='name asc')
        return product_wheel_size

    @api.multi
    def quote_vehicle_model(self):
        product_vehicle_model = request.env['sb.vehicle.model'].sudo().search([])
        return product_vehicle_model

    @api.multi
    def fetch_customers_comments(self):
        customer_comment = request.env['website.customer.comment'].sudo().search([])
        return customer_comment
