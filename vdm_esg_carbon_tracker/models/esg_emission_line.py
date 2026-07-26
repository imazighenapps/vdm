from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ESGEmissionLine(models.Model):
    _name = 'esg.emission.line'
    _description = 'ESG Emission Line'
    _order = 'date desc, sequence'

    name = fields.Char(string='Description', required=True)
    sequence = fields.Integer(default=10)
    
    inventory_id = fields.Many2one('esg.carbon.inventory', string='Carbon Inventory', 
        required=True, ondelete='cascade')
    
    emission_factor_id = fields.Many2one('esg.emission.factor', string='Emission Factor', 
        required=True, domain="[('active', '=', True)]")
    
    scope = fields.Selection([
        ('1', 'Scope 1 - Direct'),
        ('2', 'Scope 2 - Indirect Energy'),
        ('3', 'Scope 3 - Value Chain'),
    ], string='GHG Scope', required=True, related='emission_factor_id.scope')
    
    category = fields.Selection([
        ('stationary_combustion', 'Stationary Combustion'),
        ('mobile_combustion', 'Mobile Combustion'),
        ('process_emissions', 'Process Emissions'),
        ('fugitive_emissions', 'Fugitive Emissions'),
        ('purchased_energy', 'Purchased Energy'),
        ('upstream_transport', 'Upstream Transportation'),
        ('waste', 'Waste Generated'),
        ('business_travel', 'Business Travel'),
        ('employee_commuting', 'Employee Commuting'),
        ('upstream_commuting', 'Upstream Leased Assets'),
        ('downstream_transport', 'Downstream Transportation'),
        ('use_of_products', 'Use of Sold Products'),
        ('end_of_life', 'End-of-Life Treatment'),
        ('investments', 'Investments'),
        ('franchises', 'Franchises'),
        ('other', 'Other'),
    ], string='GHG Category', required=True, related='emission_factor_id.category')
    
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    activity_date = fields.Date(string='Activity Date')
    
    quantity = fields.Float(string='Activity Quantity', required=True, default=1.0)
    unit = fields.Selection([
        ('kg', 'kg'),
        ('kwh', 'kWh'),
        ('mwh', 'MWh'),
        ('liter', 'Liter'),
        ('gallon', 'Gallon'),
        ('m3', 'm³'),
        ('km', 'km'),
        ('tonne', 'Tonne'),
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ], string='Unit', related='emission_factor_id.unit')
    
    emission_factor_value = fields.Float(string='Factor Value', 
        related='emission_factor_id.factor_value')
    gas_type = fields.Selection([
        ('co2', 'CO2'),
        ('ch4', 'CH4'),
        ('n2o', 'N2O'),
        ('hfcs', 'HFCs'),
        ('pfcs', 'PFCs'),
        ('sf6', 'SF6'),
        ('nf3', 'NF3'),
    ], string='Gas Type', related='emission_factor_id.gas_type')
    
    emissions_kg = fields.Float(string='Emissions (kgCO2e)', compute='_compute_emissions', store=True)
    emissions_tco2e = fields.Float(string='Emissions (tCO2e)', compute='_compute_emissions', store=True)
    
    partner_id = fields.Many2one('res.partner', string='Supplier/Partner')
    product_id = fields.Many2one('product.product', string='Product')
    account_id = fields.Many2one('account.account', string='Account')
    
    source_document = fields.Char(string='Source Document')
    source_url = fields.Char(string='Source URL')
    
    notes = fields.Text(string='Notes')
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', tracking=True)
    
    validated_by = fields.Many2one('res.users', string='Validated By')
    validation_date = fields.Datetime(string='Validation Date')
    
    @api.depends('quantity', 'emission_factor_id')
    def _compute_emissions(self):
        for line in self:
            if line.emission_factor_id and line.quantity:
                gwp = line.emission_factor_id.gwp_value or 1.0
                line.emissions_kg = line.quantity * line.emission_factor_id.factor_value * gwp
                line.emissions_tco2e = line.emissions_kg / 1000.0
            else:
                line.emissions_kg = 0.0
                line.emissions_tco2e = 0.0
    
    def action_validate(self):
        for line in self:
            line.write({
                'state': 'validated',
                'validated_by': self.env.uid,
                'validation_date': fields.Datetime.now(),
            })
    
    def action_approve(self):
        for line in self:
            line.write({'state': 'approved'})
    
    def action_reset(self):
        for line in self:
            line.write({'state': 'draft'})
