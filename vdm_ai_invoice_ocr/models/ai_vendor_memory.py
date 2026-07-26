from odoo import models, fields, api


class AiVendorMemory(models.Model):
    _name = 'ai.vendor.memory'
    _description = 'AI Vendor Learning Memory'
    _order = 'correction_count desc'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, ondelete='cascade')
    field_name = fields.Char(string='Field', required=True)
    original_value = fields.Text(string='Original Value')
    corrected_value = fields.Text(string='Corrected Value')
    correction_count = fields.Integer(string='Corrections', default=1)
    last_correction = fields.Datetime(string='Last Correction', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('partner_field_unique', 'unique(partner_id, field_name, company_id)',
         'Memory entry already exists for this vendor and field!')
    ]

    def get_vendor_memory(self, partner_id, field_name=False):
        domain = [('partner_id', '=', partner_id)]
        if field_name:
            domain.append(('field_name', '=', field_name))
        return self.search(domain)
