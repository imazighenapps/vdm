from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ESGEmissionFactor(models.Model):
    _name = 'esg.emission.factor'
    _description = 'ESG Emission Factor'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(string='Factor Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(string='Factor Code', required=True)
    
    scope = fields.Selection([
        ('1', 'Scope 1 - Direct'),
        ('2', 'Scope 2 - Indirect Energy'),
        ('3', 'Scope 3 - Value Chain'),
    ], string='GHG Scope', required=True)
    
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
    ], string='GHG Category', required=True)
    
    fuel_type = fields.Selection([
        ('electricity', 'Electricity'),
        ('natural_gas', 'Natural Gas'),
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('fuel_oil', 'Fuel Oil'),
        ('coal', 'Coal'),
        ('lpg', 'LPG'),
        ('kerosene', 'Kerosene'),
        ('propane', 'Propane'),
        ('other', 'Other'),
    ], string='Fuel Type')
    
    gas_type = fields.Selection([
        ('co2', 'CO2'),
        ('ch4', 'CH4'),
        ('n2o', 'N2O'),
        ('hfcs', 'HFCs'),
        ('pfcs', 'PFCs'),
        ('sf6', 'SF6'),
        ('nf3', 'NF3'),
    ], string='Greenhouse Gas', required=True, default='co2')
    
    gwp_value = fields.Float(string='GWP Value', default=1.0,
        help='Global Warming Potential value for CO2-equivalent conversion')
    
    factor_value = fields.Float(string='Emission Factor Value', required=True,
        help='Emission factor in kgCO2e per unit')
    
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
    ], string='Unit', required=True)
    
    compute_method = fields.Selection([
        ('physical', 'Physical Quantity'),
        ('monetary', 'Monetary Value'),
    ], string='Compute Method', default='physical')
    
    source_database = fields.Selection([
        ('defra', 'DEFRA'),
        ('epa', 'US EPA'),
        ('ecoinvent', 'Ecoinvent'),
        ('ademe', 'ADEME'),
        ('ghg_protocol', 'GHG Protocol'),
        ('custom', 'Custom'),
    ], string='Source Database', default='custom')
    
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    
    uncertainty = fields.Float(string='Uncertainty (%)', default=10.0)
    
    country_id = fields.Many2one('res.country', string='Country/Region')
    
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('unique_factor_code', 'UNIQUE(code)', 'Emission factor code must be unique!')
    ]
    
    @api.constrains('factor_value')
    def _check_factor_value(self):
        for record in self:
            if record.factor_value < 0:
                raise ValidationError("Emission factor value cannot be negative!")
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.factor_value} {record.unit})"
            result.append((record.id, name))
        return result
