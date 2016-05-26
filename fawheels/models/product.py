# -*- coding: utf-8 -*-

from openerp import api, fields, models


class product_template(models.Model):
    _inherit = 'product.template'

    is_features = fields.Boolean(string='Features Product', default=False)
    is_arrival = fields.Boolean(string='New Arrival Product', default=False)
    show_warranty = fields.Boolean(string='Show Warranty Tab', default=True)
    warranty_details = fields.Html(string="Warranty")
    show_description_tab = fields.Boolean(string='Show Description Tab',  default=True)
    # description_details = fields.Html(string="Description")
    show_terms_and_conditions = fields.Boolean(string='Show Terms and Conditions Tab',  default=True)
    terms_and_conditions_details = fields.Html(string="Terms And Conditions")
