from datetime import datetime, timedelta
from openerp import api, fields, models, _

class sb_subprocess(models.Model):
    _name = "sb.subprocess"
    _description = "sb.subprocess"

    name = fields.Char(string = 'Name')

class sb_process_tag(models.Model):
    _name = "sb.process.tag"
    _description = "sb.process.tag"

    name = fields.Char(string ='Name')

class sb_job_process(models.Model):
    _name = "sb.job.process"
    _description = "sb.job.process"
    _order = "sequence"
    
    name = fields.Char(string = 'Name')
    subprocess_id = fields.Many2one('sb.subprocess', string ='Sub Process')
    tag_ids = fields.Many2many('sb.process.tag', 'rel_process_tag', 'newid_one', 'currentmodel_id', string = 'Tags')
    main_process = fields.Selection([('p1', 'Tyre Removal'),('p2', 'Strip Old Coating'),
                                      ('p3', 'Sand Blasting'),('p4', 'Prep & Repair Team'),
                                      ('p5', 'Ceremic Polishing'),('p6', 'Paint'),
                                      ('p7', 'Diamond Cut'),('p8', 'Lacquer'),
                                      ('p9', 'Quality Check'),('p10', 'Finished Goods'),
                                      ('p11', 'Tyre Fitting')
                                      ], string = 'Stage', required=True)
    job_order_id = fields.Many2one('sb.job.order', string ='Job Order')
    product_package_id = fields.Many2one('sb.product.package', string = 'Package')
    sequence = fields.Integer(string = 'Sequence', default= 10)
    not_include =  fields.Boolean(string = "Not Include In Workflow")

    @api.onchange('main_process')
    def onchange_main_process(self):
        for text in self.fields_get(['main_process'])['main_process']['selection']:
            if text[0] == self.main_process:self.name = text[1]
