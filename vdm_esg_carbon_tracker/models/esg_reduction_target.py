from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ESGReductionTarget(models.Model):
    _name = 'esg.reduction.target'
    _description = 'ESG Reduction Target'
    _inherit = ['mail.thread']
    _order = 'target_year, id'

    name = fields.Char(string='Target Name', required=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    target_type = fields.Selection([
        ('absolute', 'Absolute Reduction'),
        ('intensity_revenue', 'Intensity per Revenue'),
        ('intensity_employee', 'Intensity per Employee'),
        ('intensity_product', 'Intensity per Product'),
    ], string='Target Type', required=True)
    
    scope = fields.Selection([
        ('1', 'Scope 1'),
        ('2', 'Scope 2'),
        ('3', 'Scope 3'),
        ('1_2', 'Scope 1 + 2'),
        ('total', 'Total (Scope 1+2+3)'),
    ], string='Target Scope', required=True)
    
    target_year = fields.Integer(string='Target Year', required=True)
    base_year = fields.Integer(string='Base Year', required=True)
    
    base_emissions = fields.Float(string='Base Year Emissions (tCO2e)')
    target_emissions = fields.Float(string='Target Emissions (tCO2e)')
    reduction_percentage = fields.Float(string='Reduction Target (%)', 
        compute='_compute_reduction_percentage', store=True)
    
    current_emissions = fields.Float(string='Current Emissions (tCO2e)', 
        compute='_compute_current_emissions')
    progress_percentage = fields.Float(string='Progress (%)', 
        compute='_compute_progress', store=True)
    
    interim_2030 = fields.Float(string='2030 Interim Target (tCO2e)')
    interim_2035 = fields.Float(string='2035 Interim Target (tCO2e)')
    
    sbti_validated = fields.Boolean(string='SBTi Validated')
    sbti_validation_date = fields.Date(string='SBTi Validation Date')
    
    science_based = fields.Boolean(string='Science-Based Target')
    alignment_scenario = fields.Selection([
        ('1_5c', '1.5°C Pathway'),
        ('well_below_2c', 'Well Below 2°C'),
        ('2c', '2°C Pathway'),
        ('custom', 'Custom Scenario'),
    ], string='Alignment Scenario')
    
    annual_reduction_rate = fields.Float(string='Required Annual Reduction (%)', 
        compute='_compute_annual_rate')
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Notes')
    
    @api.depends('base_emissions', 'target_emissions')
    def _compute_reduction_percentage(self):
        for record in self:
            if record.base_emissions and record.base_emissions > 0:
                record.reduction_percentage = ((record.base_emissions - record.target_emissions) 
                    / record.base_emissions) * 100.0
            else:
                record.reduction_percentage = 0.0
    
    def _compute_current_emissions(self):
        for record in self:
            current = self.env['esg.carbon.inventory'].search([
                ('company_id', '=', record.company_id.id),
                ('state', '=', 'posted'),
            ], order='period_end desc', limit=1)
            record.current_emissions = current.total_emissions if current else 0.0
    
    @api.depends('base_emissions', 'current_emissions', 'target_emissions')
    def _compute_progress(self):
        for record in self:
            if record.base_emissions and record.target_emissions:
                total_reduction = record.base_emissions - record.target_emissions
                achieved_reduction = record.base_emissions - record.current_emissions
                record.progress_percentage = (achieved_reduction / total_reduction * 100.0 
                    if total_reduction > 0 else 0.0)
            else:
                record.progress_percentage = 0.0
    
    @api.depends('target_year', 'base_year', 'reduction_percentage')
    def _compute_annual_rate(self):
        for record in self:
            years = record.target_year - record.base_year
            if years > 0 and record.reduction_percentage:
                record.annual_reduction_rate = record.reduction_percentage / years
            else:
                record.annual_reduction_rate = 0.0
    
    def action_activate(self):
        self.write({'status': 'active'})
    
    def action_achieve(self):
        self.write({'status': 'achieved'})
    
    def action_cancel(self):
        self.write({'status': 'cancelled'})
    
    @api.constrains('target_year', 'base_year')
    def _check_years(self):
        for record in self:
            if record.target_year <= record.base_year:
                raise ValidationError("Target year must be after base year!")
    
    @api.constrains('base_emissions')
    def _check_base_emissions(self):
        for record in self:
            if record.base_emissions < 0:
                raise ValidationError("Base emissions cannot be negative!")
