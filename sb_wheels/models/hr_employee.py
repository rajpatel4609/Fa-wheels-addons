
from openerp import api, fields, models, _

class hr_employee(models.Model):
    _inherit = "hr.employee"

    sb_ni_no = fields.Char(string = 'National Insurance (NI) No.')
    sb_nh_no = fields.Char(string = 'National Health Service (NHS) No.')
    sb_kin_name = fields.Char(string = 'Next of Kin Name:')
    sb_kin_tel = fields.Char(string = 'Next of Kin Contact Telephone No:')
    sb_joindate = fields.Date(string = 'Company Join')
    sb_disjoindate = fields.Date(string = 'Company Leave Join')
    sb_disjoin_note = fields.Char(string = 'Company Leave Reason')