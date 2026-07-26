from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ESGCarbonInventory(models.Model):
    _name = 'esg.carbon.inventory'
    _description = 'ESG Carbon Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'period_start desc, id'

    name = fields.Char(string='Reference', readonly=True, copy=False, default='New')
    
    company_id = fields.Many2one('res.company', string='Company', 
        default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    
    period_start = fields.Date(string='Period Start', required=True)
    period_end = fields.Date(string='Period End', required=True)
    period_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period Type', default='yearly')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('collecting', 'Data Collection'),
        ('calculating', 'Calculating'),
        ('validated', 'Validated'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    emission_line_ids = fields.One2many('esg.emission.line', 'inventory_id', string='Emission Lines')
    emission_line_count = fields.Integer(compute='_compute_emission_line_count')
    
    scope1_total = fields.Float(string='Scope 1 Total (tCO2e)', compute='_compute_scope_totals', store=True)
    scope2_total = fields.Float(string='Scope 2 Total (tCO2e)', compute='_compute_scope_totals', store=True)
    scope3_total = fields.Float(string='Scope 3 Total (tCO2e)', compute='_compute_scope_totals', store=True)
    
    total_emissions = fields.Float(string='Total Emissions (tCO2e)', compute='_compute_total_emissions', store=True)
    
    scope1_stationary = fields.Float(string='Stationary Combustion', compute='_compute_category_totals', store=True)
    scope1_mobile = fields.Float(string='Mobile Combustion', compute='_compute_category_totals', store=True)
    scope1_process = fields.Float(string='Process Emissions', compute='_compute_category_totals', store=True)
    scope1_fugitive = fields.Float(string='Fugitive Emissions', compute='_compute_category_totals', store=True)
    
    scope2_electricity = fields.Float(string='Purchased Electricity', compute='_compute_category_totals', store=True)
    scope2_heat = fields.Float(string='Purchased Heat/Steam', compute='_compute_category_totals', store=True)
    
    intensity_per_revenue = fields.Float(string='tCO2e per €M Revenue', compute='_compute_intensity', store=True)
    intensity_per_employee = fields.Float(string='tCO2e per Employee', compute='_compute_intensity', store=True)
    
    revenue_amount = fields.Monetary(string='Revenue Amount', currency_field='currency_id')
    employee_count = fields.Integer(string='Employee Count')
    
    base_year_emissions = fields.Float(string='Base Year Emissions (tCO2e)')
    reduction_vs_base = fields.Float(string='Reduction vs Base Year (%)', compute='_compute_reduction', store=True)
    
    anomaly_flag = fields.Boolean(string='Anomaly Detected', default=False)
    anomaly_notes = fields.Text(string='Anomaly Notes')
    
    notes = fields.Html(string='Notes')
    
    validated_by = fields.Many2one('res.users', string='Validated By')
    validation_date = fields.Datetime(string='Validation Date')
    
    posted_date = fields.Datetime(string='Posted Date')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('esg.carbon.inventory') or 'New'
        return super().create(vals_list)
    
    def _compute_emission_line_count(self):
        for record in self:
            record.emission_line_count = len(record.emission_line_ids)
    
    @api.depends('emission_line_ids.emissions_tco2e', 'emission_line_ids.scope')
    def _compute_scope_totals(self):
        for record in self:
            lines = record.emission_line_ids
            record.scope1_total = sum(l.emissions_tco2e for l in lines if l.scope == '1')
            record.scope2_total = sum(l.emissions_tco2e for l in lines if l.scope == '2')
            record.scope3_total = sum(l.emissions_tco2e for l in lines if l.scope == '3')
    
    @api.depends('scope1_total', 'scope2_total', 'scope3_total')
    def _compute_total_emissions(self):
        for record in self:
            record.total_emissions = record.scope1_total + record.scope2_total + record.scope3_total
    
    @api.depends('emission_line_ids.emissions_tco2e', 'emission_line_ids.category')
    def _compute_category_totals(self):
        for record in self:
            lines = record.emission_line_ids
            record.scope1_stationary = sum(l.emissions_tco2e for l in lines if l.category == 'stationary_combustion')
            record.scope1_mobile = sum(l.emissions_tco2e for l in lines if l.category == 'mobile_combustion')
            record.scope1_process = sum(l.emissions_tco2e for l in lines if l.category == 'process_emissions')
            record.scope1_fugitive = sum(l.emissions_tco2e for l in lines if l.category == 'fugitive_emissions')
            record.scope2_electricity = sum(l.emissions_tco2e for l in lines if l.category == 'purchased_energy')
            record.scope2_heat = 0.0
    
    @api.depends('total_emissions', 'revenue_amount', 'employee_count', 'company_id.currency_id')
    def _compute_intensity(self):
        for record in self:
            if record.revenue_amount and record.company_id.currency_id:
                rate = self.env.company.currency_id.rate or 1.0
                revenue_eur = record.revenue_amount / rate if rate else record.revenue_amount
                revenue_million = revenue_eur / 1_000_000.0
                record.intensity_per_revenue = record.total_emissions / revenue_million if revenue_million else 0.0
            else:
                record.intensity_per_revenue = 0.0
            
            if record.employee_count:
                record.intensity_per_employee = record.total_emissions / record.employee_count
            else:
                record.intensity_per_employee = 0.0
    
    @api.depends('total_emissions', 'base_year_emissions')
    def _compute_reduction(self):
        for record in self:
            if record.base_year_emissions and record.base_year_emissions > 0:
                record.reduction_vs_base = ((record.base_year_emissions - record.total_emissions) 
                    / record.base_year_emissions) * 100.0
            else:
                record.reduction_vs_base = 0.0
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    def action_collecting(self):
        self.write({'state': 'collecting'})
    
    def action_calculating(self):
        self._compute_scope_totals()
        self._compute_total_emissions()
        self._compute_category_totals()
        self._compute_intensity()
        self._detect_anomalies()
        self.write({'state': 'calculating'})
    
    def action_validate(self):
        self.write({
            'state': 'validated',
            'validated_by': self.env.uid,
            'validation_date': fields.Datetime.now(),
        })
    
    def action_post(self):
        self.write({
            'state': 'posted',
            'posted_date': fields.Datetime.now(),
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def _detect_anomalies(self):
        config = self.env['esg.config'].search([('company_id', '=', self.company_id.id)], limit=1)
        if config and config.anomaly_detection:
            threshold = config.anomaly_threshold or 20.0
            previous = self.search([
                ('company_id', '=', self.company_id.id),
                ('state', '=', 'posted'),
                ('id', '!=', self.id),
            ], order='period_end desc', limit=1)
            
            if previous and previous.total_emissions > 0:
                change_pct = abs((self.total_emissions - previous.total_emissions) 
                    / previous.total_emissions) * 100.0
                
                if change_pct > threshold:
                    self.write({
                        'anomaly_flag': True,
                        'anomaly_notes': f'Emissions changed by {change_pct:.1f}% compared to previous period. '
                            f'Previous: {previous.total_emissions:.2f} tCO2e, Current: {self.total_emissions:.2f} tCO2e',
                    })
    
    def action_view_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Emission Lines',
            'res_model': 'esg.emission.line',
            'view_mode': 'list,form',
            'domain': [('inventory_id', '=', self.id)],
            'context': {'default_inventory_id': self.id},
        }
