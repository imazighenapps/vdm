# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    audit_enable_logging = fields.Boolean(
        string='Enable Audit Logging',
        config_parameter='audit_trail_pro.enable_logging',
        default=True,
    )
    audit_log_retention = fields.Selection([
        ('3months', '3 Months'),
        ('6months', '6 Months'),
        ('12months', '12 Months'),
        ('24months', '24 Months'),
        ('never', 'Never Delete'),
    ], string='Log Retention Period',
        config_parameter='audit_trail_pro.retention_period',
        default='12months',
    )
    audit_enable_alerts = fields.Boolean(
        string='Enable Alerts',
        config_parameter='audit_trail_pro.enable_alerts',
        default=True,
    )
    audit_enable_risk_scoring = fields.Boolean(
        string='Enable Risk Scoring',
        config_parameter='audit_trail_pro.enable_risk_scoring',
        default=True,
    )

    def action_open_audit_config(self):
        """Open audit configuration."""
        config = self.env['audit.trail.config'].sudo().get_config()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Audit Trail Configuration',
            'res_model': 'audit.trail.config',
            'res_id': config.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_audit_logs(self):
        """View audit logs."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Audit Logs',
            'res_model': 'audit.trail.log',
            'view_mode': 'list,form,pivot,graph,calendar',
            'target': 'current',
        }

    def action_view_dashboard(self):
        """View audit dashboard."""
        return {
            'type': 'ir.actions.client',
            'tag': 'audit_trail_dashboard',
            'target': 'current',
        }
