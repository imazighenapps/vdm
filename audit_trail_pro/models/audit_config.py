# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AuditTrailConfig(models.Model):
    _name = 'audit.trail.config'
    _description = 'Audit Trail Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    # General settings
    enable_logging = fields.Boolean(string='Enable Audit Logging', default=True, tracking=True)
    
    # Action logging
    log_create = fields.Boolean(string='Log Creates', default=True, tracking=True)
    log_update = fields.Boolean(string='Log Updates', default=True, tracking=True)
    log_delete = fields.Boolean(string='Log Deletes', default=True, tracking=True)
    log_read = fields.Boolean(string='Log Reads', default=False, tracking=True)
    log_exports = fields.Boolean(string='Log Exports', default=True, tracking=True)
    log_prints = fields.Boolean(string='Log Prints', default=True, tracking=True)
    log_emails = fields.Boolean(string='Log Emails', default=True, tracking=True)
    log_connections = fields.Boolean(string='Log Connections', default=True, tracking=True)
    log_rights = fields.Boolean(string='Log Rights Changes', default=True, tracking=True)
    log_settings = fields.Boolean(string='Log Settings Changes', default=True, tracking=True)
    log_reads_detailed = fields.Boolean(string='Detailed Read Logging', default=False, tracking=True,
        help='Log every record read (can generate many logs)')
    
    # Model filtering
    model_filter_type = fields.Selection([
        ('blacklist', 'Blacklist (exclude specific models)'),
        ('whitelist', 'Whitelist (only specific models)'),
    ], string='Model Filter', default='blacklist', tracking=True)
    excluded_model_ids = fields.Many2many('ir.model', 'audit_config_excluded_model_rel', string='Excluded Models', tracking=True)
    included_model_ids = fields.Many2many('ir.model', 'audit_config_included_model_rel', string='Included Models', tracking=True)
    
    # Field filtering
    excluded_field_ids = fields.Many2many('ir.model.fields', string='Excluded Fields', tracking=True,
        help='Fields to exclude from logging (e.g., write_uid, write_date)')
    
    # Retention
    retention_period = fields.Selection([
        ('3months', '3 Months'),
        ('6months', '6 Months'),
        ('12months', '12 Months'),
        ('24months', '24 Months'),
        ('never', 'Never Delete'),
    ], string='Log Retention Period', default='12months', tracking=True)
    
    # Risk scoring
    enable_risk_scoring = fields.Boolean(string='Enable Risk Scoring', default=True, tracking=True)
    
    # Alerts
    enable_alerts = fields.Boolean(string='Enable Alerts', default=True, tracking=True)
    
    # Dashboard
    enable_dashboard = fields.Boolean(string='Enable Dashboard', default=True, tracking=True)
    
    # Default severity
    default_severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Default Severity', default='low', tracking=True)

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Configuration must be unique per company!'),
    ]

    @api.model
    def get_config(self):
        """Get or create configuration for current company."""
        config = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not config:
            config = self.create([{'company_id': self.env.company.id}])
        return config

    def action_reset_defaults(self):
        """Reset configuration to default values."""
        self.ensure_one()
        defaults = {
            'enable_logging': True,
            'log_create': True,
            'log_update': True,
            'log_delete': True,
            'log_read': False,
            'log_exports': True,
            'log_prints': True,
            'log_emails': True,
            'log_connections': True,
            'log_rights': True,
            'log_settings': True,
            'log_reads_detailed': False,
            'model_filter_type': 'blacklist',
            'retention_period': '12months',
            'enable_risk_scoring': True,
            'enable_alerts': True,
            'enable_dashboard': True,
            'default_severity': 'low',
        }
        self.write(defaults)
        self.excluded_model_ids = [(5, 0, 0)]
        self.included_model_ids = [(5, 0, 0)]
        self.excluded_field_ids = [(5, 0, 0)]

    def action_view_logs(self):
        """View all audit logs."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Audit Logs',
            'res_model': 'audit.trail.log',
            'view_mode': 'list,form,pivot,graph,calendar',
            'target': 'current',
        }

    def action_view_alerts(self):
        """View all alerts."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Audit Alerts',
            'res_model': 'audit.trail.alert',
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_cleanup_now(self):
        """Trigger immediate cleanup."""
        self.env['audit.trail.log'].sudo().cleanup_old_logs()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cleanup Complete',
                'message': 'Old audit logs have been cleaned up.',
                'sticky': False,
                'type': 'success',
            }
        }
