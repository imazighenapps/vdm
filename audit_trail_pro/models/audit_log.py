# -*- coding: utf-8 -*-
import json
import logging
import traceback
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied
from odoo.http import request, root as http_root

_logger = logging.getLogger(__name__)


class AuditTrailLog(models.Model):
    _name = 'audit.trail.log'
    _description = 'Audit Trail Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # Core fields
    name = fields.Char(string='Description', required=True, tracking=True)
    sequence = fields.Char(string='Sequence', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # User info
    user_id = fields.Many2one('res.users', string='User', required=True, tracking=True, index=True)
    login = fields.Char(string='Login', related='user_id.login', store=True, index=True)
    
    # Record info
    model_name = fields.Char(string='Model', required=True, index=True)
    model_id = fields.Many2one('ir.model', string='Odoo Model', compute='_compute_model_id', store=True)
    record_id = fields.Integer(string='Record ID', index=True)
    record_name = fields.Char(string='Record Name', index=True)
    
    # Action info
    action_type = fields.Selection([
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('read', 'Read'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('email', 'Email'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('rights_change', 'Rights Change'),
        ('settings_change', 'Settings Change'),
    ], string='Action Type', required=True, index=True)
    
    # Change details
    field_name = fields.Char(string='Field', index=True)
    field_label = fields.Char(string='Field Label')
    old_value = fields.Text(string='Old Value')
    new_value = fields.Text(string='New Value')
    change_json = fields.Text(string='Change Details (JSON)')
    
    # Context info
    ip_address = fields.Char(string='IP Address', index=True)
    browser = fields.Char(string='Browser', index=True)
    operating_system = fields.Char(string='Operating System')
    session_id = fields.Char(string='Session ID')
    http_request = fields.Text(string='HTTP Request')
    
    # Risk assessment
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Severity', default='low', index=True, tracking=True)
    risk_score = fields.Integer(string='Risk Score', default=0, index=True)
    
    # Additional info
    notes = fields.Text(string='Notes')
    tags = fields.Char(string='Tags', index=True)
    
    # Technical
    duration = fields.Float(string='Duration (ms)')
    stack_trace = fields.Text(string='Stack Trace')
    
    # Computed
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    
    _sql_constraints = [
        ('sequence_uniq', 'unique(sequence, company_id)', 'Sequence must be unique per company!'),
    ]

    @api.depends('model_name')
    def _compute_model_id(self):
        for rec in self:
            model = self.env['ir.model'].search([('model', '=', rec.model_name)], limit=1)
            rec.model_id = model.id if model else False

    @api.depends('action_type', 'model_name', 'record_name', 'user_id')
    def _compute_display_name(self):
        for rec in self:
            action_labels = {
                'create': 'Created',
                'update': 'Updated',
                'delete': 'Deleted',
                'read': 'Read',
                'export': 'Exported',
                'print': 'Printed',
                'email': 'Email Sent',
                'login': 'Login',
                'logout': 'Logout',
                'login_failed': 'Login Failed',
                'rights_change': 'Rights Changed',
                'settings_change': 'Settings Changed',
            }
            action = action_labels.get(rec.action_type, rec.action_type)
            model = rec.model_name or ''
            record = rec.record_name or str(rec.record_id) or ''
            user = rec.user_id.name or ''
            rec.display_name = f"[{action}] {model} - {record} by {user}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('audit.trail.log') or '/'
        return super().create(vals_list)

    @api.model
    def _get_request_info(self):
        """Extract request information from the current HTTP request."""
        try:
            if request and hasattr(request, 'httprequest'):
                httprequest = request.httprequest
                return {
                    'ip_address': httprequest.remote_addr or '',
                    'browser': httprequest.user_agent.string or '',
                    'operating_system': str(httprequest.user_agent.platform or ''),
                    'session_id': request.session.sid or '',
                    'http_request': f"{httprequest.method} {httprequest.path}",
                }
        except Exception:
            pass
        return {
            'ip_address': '',
            'browser': '',
            'operating_system': '',
            'session_id': '',
            'http_request': '',
        }

    @api.model
    def _log_action(self, action_type, model_name, record_id=0, record_name='',
                    field_name='', old_value='', new_value='', notes='',
                    severity='low', risk_score=0, tags=''):
        """Main method to create audit log entries."""
        config = self.env['audit.trail.config'].sudo().get_config()
        
        # Check if logging is enabled for this action
        if not config or not config.enable_logging:
            return False
        
        # Check model filter
        if config.model_filter_type == 'blacklist' and model_name in config.excluded_model_ids.mapped('model'):
            return False
        if config.model_filter_type == 'whitelist' and model_name not in config.included_model_ids.mapped('model'):
            return False
        
        # Check specific action logging
        action_map = {
            'create': config.log_create,
            'update': config.log_update,
            'delete': config.log_delete,
            'read': config.log_read,
            'export': config.log_exports,
            'print': config.log_prints,
            'email': config.log_emails,
            'login': config.log_connections,
            'logout': config.log_connections,
            'login_failed': config.log_connections,
            'rights_change': config.log_rights,
            'settings_change': config.log_settings,
        }
        if not action_map.get(action_type, True):
            return False
        
        # Get request info
        request_info = self._get_request_info()
        
        # Prepare values
        vals = {
            'name': f"{action_type.upper()} on {model_name}",
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
            'model_name': model_name,
            'record_id': record_id,
            'record_name': record_name or '',
            'action_type': action_type,
            'field_name': field_name or '',
            'field_label': self._get_field_label(model_name, field_name) if field_name else '',
            'old_value': str(old_value) if old_value else '',
            'new_value': str(new_value) if new_value else '',
            'notes': notes or '',
            'severity': severity,
            'risk_score': risk_score,
            'tags': tags or '',
            'ip_address': request_info.get('ip_address', ''),
            'browser': request_info.get('browser', ''),
            'operating_system': request_info.get('operating_system', ''),
            'session_id': request_info.get('session_id', ''),
            'http_request': request_info.get('http_request', ''),
        }
        
        # Add JSON details for updates
        if action_type == 'update' and field_name and (old_value or new_value):
            change_details = {
                'field': field_name,
                'old': old_value,
                'new': new_value,
            }
            vals['change_json'] = json.dumps(change_details, default=str)
        
        try:
            log = self.sudo().create([vals])
            # Check alerts
            self.env['audit.trail.alert'].sudo().check_alerts(log)
            return log
        except Exception as e:
            _logger.error(f"Audit Trail: Failed to log action: {e}")
            return False

    def _get_field_label(self, model_name, field_name):
        """Get human-readable field label."""
        try:
            model = self.env['ir.model'].sudo().search([('model', '=', model_name)], limit=1)
            if model:
                field = self.env[model.model]._fields.get(field_name)
                if field:
                    return field.string or field_name
        except Exception:
            pass
        return field_name

    @api.model
    def log_create(self, model_name, record):
        """Log record creation."""
        record_name = getattr(record, 'name', False) or getattr(record, 'display_name', False) or str(record.id)
        return self._log_action(
            action_type='create',
            model_name=model_name,
            record_id=record.id,
            record_name=record_name,
        )

    @api.model
    def log_write(self, model_name, record, vals):
        """Log record modification with field details."""
        logs = []
        for field_name, new_value in vals.items():
            old_value = getattr(record, field_name, None)
            if old_value != new_value:
                # Check if field is in excluded list
                config = self.env['audit.trail.config'].sudo().get_config()
                if config and field_name in config.excluded_field_ids.mapped('name'):
                    continue
                
                severity = self._assess_severity(model_name, field_name, old_value, new_value)
                risk_score = self._calculate_risk_score('update', model_name, field_name)
                
                log = self._log_action(
                    action_type='update',
                    model_name=model_name,
                    record_id=record.id,
                    record_name=getattr(record, 'name', False) or str(record.id),
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    severity=severity,
                    risk_score=risk_score,
                )
                if log:
                    logs.append(log)
        return logs

    @api.model
    def log_unlink(self, model_name, record):
        """Log record deletion."""
        record_name = getattr(record, 'name', False) or getattr(record, 'display_name', False) or str(record.id)
        
        # Capture all important values before deletion
        important_fields = ['name', 'display_name', 'state', 'amount_total', 'partner_id']
        values_captured = {}
        for field_name in important_fields:
            if hasattr(record, field_name):
                values_captured[field_name] = str(getattr(record, field_name, ''))
        
        severity = 'high' if 'invoice' in model_name.lower() or 'payment' in model_name.lower() else 'medium'
        risk_score = self._calculate_risk_score('delete', model_name)
        
        return self._log_action(
            action_type='delete',
            model_name=model_name,
            record_id=record.id,
            record_name=record_name,
            old_value=json.dumps(values_captured, default=str),
            notes=f"Record deleted. Captured values: {list(values_captured.keys())}",
            severity=severity,
            risk_score=risk_score,
        )

    @api.model
    def log_read(self, model_name, record):
        """Log record read access."""
        config = self.env['audit.trail.config'].sudo().get_config()
        if not config or not config.log_reads_detailed:
            return False
        
        record_name = getattr(record, 'name', False) or str(record.id)
        return self._log_action(
            action_type='read',
            model_name=model_name,
            record_id=record.id,
            record_name=record_name,
        )

    @api.model
    def log_export(self, model_name, record_count=0, export_type='excel'):
        """Log export action."""
        return self._log_action(
            action_type='export',
            model_name=model_name,
            notes=f"Export {export_type}: {record_count} records",
            severity='medium' if record_count > 100 else 'low',
            risk_score=15 if record_count > 100 else 5,
            tags=export_type,
        )

    @api.model
    def log_print(self, model_name, record_id=0, report_name=''):
        """Log print action."""
        return self._log_action(
            action_type='print',
            model_name=model_name,
            record_id=record_id,
            notes=f"Printed report: {report_name}",
        )

    @api.model
    def log_email(self, model_name, record_id=0, recipient=''):
        """Log email sent."""
        return self._log_action(
            action_type='email',
            model_name=model_name,
            record_id=record_id,
            notes=f"Email sent to: {recipient}",
        )

    @api.model
    def log_connection(self, login, success=True, ip_address='', browser='', os=''):
        """Log connection attempt."""
        user = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        
        action_type = 'login' if success else 'login_failed'
        severity = 'low' if success else 'high'
        risk_score = 0 if success else 10
        
        return self._log_action(
            action_type=action_type,
            model_name='res.users',
            record_id=user.id if user else 0,
            record_name=login,
            ip_address=ip_address,
            browser=browser,
            operating_system=os,
            severity=severity,
            risk_score=risk_score,
        )

    @api.model
    def log_rights_change(self, model_name, record_id=0, details=''):
        """Log rights/access change."""
        return self._log_action(
            action_type='rights_change',
            model_name=model_name,
            record_id=record_id,
            notes=details,
            severity='critical',
            risk_score=40,
        )

    @api.model
    def log_settings_change(self, model_name, record_id=0, details=''):
        """Log settings change."""
        return self._log_action(
            action_type='settings_change',
            model_name=model_name,
            record_id=record_id,
            notes=details,
            severity='high',
            risk_score=25,
        )

    def _assess_severity(self, model_name, field_name, old_value, new_value):
        """Assess the severity of a change."""
        # High-risk fields
        high_risk_fields = ['password', 'active', 'admin', 'group_ids', 'access Rights']
        if field_name in high_risk_fields:
            return 'critical'
        
        # High-risk models
        high_risk_models = ['account.move', 'account.payment', 'res.users', 'res.partner']
        if model_name in high_risk_models:
            return 'high'
        
        # Amount changes
        if 'amount' in field_name.lower() or 'price' in field_name.lower():
            try:
                old_val = float(old_value) if old_value else 0
                new_val = float(new_value) if new_value else 0
                if abs(new_val - old_val) > 1000:
                    return 'high'
                elif abs(new_val - old_val) > 100:
                    return 'medium'
            except (ValueError, TypeError):
                pass
        
        return 'low'

    def _calculate_risk_score(self, action_type, model_name, field_name=''):
        """Calculate risk score for an action."""
        base_scores = {
            'create': 5,
            'update': 10,
            'delete': 20,
            'read': 1,
            'export': 15,
            'print': 3,
            'email': 5,
            'login': 0,
            'logout': 0,
            'login_failed': 10,
            'rights_change': 40,
            'settings_change': 25,
        }
        
        score = base_scores.get(action_type, 5)
        
        # Model multiplier
        high_risk_models = ['account.move', 'account.payment', 'res.users']
        if model_name in high_risk_models:
            score *= 2
        
        # Field multiplier
        critical_fields = ['password', 'group_ids', 'admin']
        if field_name in critical_fields:
            score *= 3
        
        return min(score, 100)

    @api.model
    def cleanup_old_logs(self):
        """Cron job to cleanup old audit logs."""
        config = self.env['audit.trail.config'].sudo().get_config()
        if not config or config.retention_period == 'never':
            return
        
        retention_map = {
            '3months': 90,
            '6months': 180,
            '12months': 365,
            '24months': 730,
        }
        
        days = retention_map.get(config.retention_period, 365)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        old_logs = self.search([('create_date', '<', cutoff_date)])
        if old_logs:
            count = len(old_logs)
            old_logs.unlink()
            _logger.info(f"Audit Trail: Cleaned up {count} old log entries")

    def action_view_record(self):
        """Open the related record."""
        self.ensure_one()
        if self.model_name and self.record_id:
            try:
                model = self.env[self.model_name]
                record = model.browse(self.record_id)
                if record.exists():
                    return {
                        'type': 'ir.actions.act_window',
                        'name': self.record_name or self.model_name,
                        'res_model': self.model_name,
                        'res_id': self.record_id,
                        'view_mode': 'form',
                        'target': 'current',
                    }
            except Exception:
                pass
        return False

    def action_view_user(self):
        """Open the related user."""
        self.ensure_one()
        if self.user_id:
            return {
                'type': 'ir.actions.act_window',
                'name': self.user_id.name,
                'res_model': 'res.users',
                'res_id': self.user_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_export_logs(self):
        """Export logs to CSV."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Audit Logs',
            'res_model': 'audit.log.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids},
        }
