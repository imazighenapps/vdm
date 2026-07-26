from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ESGCarbonOffset(models.Model):
    _name = 'esg.carbon.offset'
    _description = 'ESG Carbon Offset'
    _inherit = ['mail.thread']
    _order = 'vintage_year desc, id'

    name = fields.Char(string='Offset Reference', required=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    project_name = fields.Char(string='Project Name', required=True)
    project_type = fields.Selection([
        ('reforestation', 'Reforestation/Afforestation'),
        ('renewable_energy', 'Renewable Energy'),
        ('methane_capture', 'Methane Capture'),
        ('cookstoves', 'Clean Cookstoves'),
        ('water', 'Water Purification'),
        ('waste', 'Waste Management'),
        ('other', 'Other'),
    ], string='Project Type', required=True)
    
    standard = fields.Selection([
        ('gs', 'Gold Standard'),
        ('vcs', 'Verra VCS'),
        ('acr', 'American Carbon Registry'),
        ('car', 'Climate Action Reserve'),
        ('other', 'Other'),
    ], string='Standard/Certification', required=True)
    
    total_credits = fields.Float(string='Total Credits Purchased (tCO2e)', required=True)
    retired_credits = fields.Float(string='Credits Retired (tCO2e)', default=0.0)
    available_credits = fields.Float(string='Available Credits (tCO2e)', 
        compute='_compute_available_credits', store=True)
    
    vintage_year = fields.Integer(string='Vintage Year', required=True)
    purchase_date = fields.Date(string='Purchase Date')
    retirement_date = fields.Date(string='Retirement Date')
    
    retirement_reason = fields.Selection([
        ('offset', 'Carbon Offset'),
        ('compliance', 'Compliance'),
        ('voluntary', 'Voluntary'),
    ], string='Retirement Reason')
    
    retirement_certificate = fields.Char(string='Retirement Certificate #')
    
    unit_price = fields.Monetary(string='Unit Price per tCO2e', currency_field='currency_id')
    total_cost = fields.Monetary(string='Total Cost', currency_field='currency_id', 
        compute='_compute_total_cost', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    
    project_country_id = fields.Many2one('res.country', string='Project Country')
    project_region = fields.Char(string='Project Region')
    
    verification_body = fields.Char(string='Verification Body')
    verification_date = fields.Date(string='Verification Date')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('purchased', 'Purchased'),
        ('partially_retired', 'Partially Retired'),
        ('fully_retired', 'Fully Retired'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Notes')
    
    @api.depends('total_credits', 'retired_credits')
    def _compute_available_credits(self):
        for record in self:
            record.available_credits = record.total_credits - record.retired_credits
    
    @api.depends('total_credits', 'unit_price')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.total_credits * record.unit_price
    
    @api.constrains('total_credits', 'retired_credits')
    def _check_credits(self):
        for record in self:
            if record.retired_credits > record.total_credits:
                raise ValidationError("Retired credits cannot exceed total credits!")
    
    def action_purchase(self):
        self.write({'state': 'purchased'})
    
    def action_retire(self):
        if self.available_credits > 0:
            self.retired_credits = self.total_credits
            self.write({
                'state': 'fully_retired',
                'retirement_date': fields.Date.today(),
            })
    
    def action_partial_retire(self):
        pass
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} - {record.project_name}"
            result.append((record.id, name))
        return result
