# -*- coding: utf-8 -*-

from openerp import api, fields, models

class FawheelsBlogPost(models.Model):
    _inherit = "blog.post"

    post_image = fields.Binary(string="Blog post Image")
