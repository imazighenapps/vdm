from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ESGConfig(models.Model):
    _name = 'esg.config'
    _description = 'ESG Configuration'
    _inherits = {'res.company': 'company_id'}

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade')
    
    base_year = fields.Integer(string='Base Year', default=2024)
    reporting_currency_id = fields.Many2one('res.currency', string='Reporting Currency')
    
    scope1_enabled = fields.Boolean(string='Track Scope 1', default=True)
    scope2_enabled = fields.Boolean(string='Track Scope 2', default=True)
    scope3_enabled = fields.Boolean(string='Track Scope 3', default=True)
    
    sbti_aligned = fields.Boolean(string='SBTi Aligned Targets')
    csrd_reporting = fields.Boolean(string='CSRD Reporting Required')
    
    emission_factor_source = fields.Selection([
        ('defra', 'DEFRA'),
        ('epa', 'US EPA'),
        ('ecoinvent', 'Ecoinvent'),
        ('ademe', 'ADEME'),
        ('custom', 'Custom Factors'),
    ], string='Default Emission Factor Source', default='defra')
    
    anomaly_detection = fields.Boolean(string='Enable Anomaly Detection', default=True)
    anomaly_threshold = fields.Float(string='Anomaly Threshold (%)', default=20.0)
    
    total_scope1 = fields.Float(string='Total Scope 1 (tCO2e)', compute='_compute_totals')
    total_scope2 = fields.Float(string='Total Scope 2 (tCO2e)', compute='_compute_totals')
    total_scope3 = fields.Float(string='Total Scope 3 (tCO2e)', compute='_compute_totals')
    total_emissions = fields.Float(string='Total Emissions (tCO2e)', compute='_compute_totals')
    
    @api.depends('company_id')
    def _compute_totals(self):
        for record in self:
            inventories = self.env['esg.carbon.inventory'].search([
                ('company_id', '=', record.company_id.id),
                ('state', '=', 'posted'),
            ])
            record.total_scope1 = sum(inventories.mapped('scope1_total'))
            record.total_scope2 = sum(inventories.mapped('scope2_total'))
            record.total_scope3 = sum(inventories.mapped('scope3_total'))
            record.total_emissions = record.total_scope1 + record.total_scope2 + record.total_scope3
