# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AuditTrailAlert(models.Model):
    _name = 'audit.trail.alert'
    _description = 'Audit Trail Alert'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Alert Name', required=True, tracking=True)
    sequence = fields.Char(string='Sequence', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # Alert configuration
    alert_type = fields.Selection([
        ('bulk_delete', 'Bulk Deletion'),
        ('bulk_export', 'Bulk Export'),
        ('new_ip', 'New IP Address'),
        ('off_hours', 'Off-Hours Activity'),
        ('rights_change', 'Rights Change'),
        ('invoice_delete', 'Invoice Deletion'),
        ('payment_cancel', 'Payment Cancellation'),
        ('massive_modification', 'Massive Modification'),
        ('failed_login', 'Failed Login Attempts'),
        ('custom', 'Custom Rule'),
    ], string='Alert Type', required=True, tracking=True)
    
    # Conditions
    threshold = fields.Integer(string='Threshold', default=10, tracking=True,
        help='Number of actions that triggers the alert')
    time_window = fields.Integer(string='Time Window (minutes)', default=60, tracking=True,
        help='Time window in minutes to check for threshold')
    
    # Filters
    model_ids = fields.Many2many('ir.model', string='Models', tracking=True,
        help='Specific models to monitor (leave empty for all)')
    user_ids = fields.Many2many('res.users', string='Users', tracking=True,
        help='Specific users to monitor (leave empty for all)')
    
    # Severity
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Severity', default='high', tracking=True)
    
    # Status
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('triggered', 'Triggered'),
    ], string='Status', default='active', tracking=True)
    
    # Actions
    notify_email = fields.Boolean(string='Send Email', default=True, tracking=True)
    notify_users = fields.Many2many('res.users', string='Notify Users', tracking=True)
    email_partner_ids = fields.Many2many('res.partner', string='Notify Partners', tracking=True)
    
    # Triggered info
    last_triggered = fields.Datetime(string='Last Triggered', readonly=True, tracking=True)
    trigger_count = fields.Integer(string='Trigger Count', default=0, readonly=True, tracking=True)
    last_log_ids = fields.One2many('audit.trail.log', string='Related Logs', compute='_compute_last_logs')
    
    # Notes
    notes = fields.Text(string='Notes', tracking=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Alert name must be unique per company!'),
    ]

    def _compute_last_logs(self):
        for alert in self:
            alert.last_log_ids = self.env['audit.trail.log'].search([], limit=10)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('audit.trail.alert') or '/'
        return super().create(vals_list)

    def action_activate(self):
        self.write({'state': 'active'})

    def action_deactivate(self):
        self.write({'state': 'inactive'})

    def action_reset(self):
        self.write({'state': 'active', 'trigger_count': 0, 'last_triggered': False})

    @api.model
    def check_alerts(self, log):
        """Check if any alert conditions are met after a new log entry."""
        alerts = self.search([('state', '=', 'active')])
        
        for alert in alerts:
            try:
                if alert._check_condition(log):
                    alert._trigger_alert(log)
            except Exception as e:
                _logger.error(f"Audit Trail Alert: Error checking alert {alert.name}: {e}")

    def _check_condition(self, log):
        """Check if the alert condition is met."""
        self.ensure_one()
        
        # Check model filter
        if self.model_ids and log.model_name not in self.model_ids.mapped('model'):
            return False
        
        # Check user filter
        if self.user_ids and log.user_id not in self.user_ids:
            return False
        
        # Calculate time window
        time_limit = datetime.now() - timedelta(minutes=self.time_window)
        
        # Build domain
        domain = [
            ('create_date', '>=', time_limit),
            ('company_id', '=', self.company_id.id),
        ]
        
        if self.model_ids:
            domain.append(('model_name', 'in', self.model_ids.mapped('model')))
        
        if self.user_ids:
            domain.append(('user_id', 'in', self.user_ids.ids))
        
        # Check by alert type
        if self.alert_type == 'bulk_delete':
            domain.append(('action_type', '=', 'delete'))
            count = self.env['audit.trail.log'].sudo().search_count(domain)
            return count >= self.threshold
        
        elif self.alert_type == 'bulk_export':
            domain.append(('action_type', '=', 'export'))
            count = self.env['audit.trail.log'].sudo().search_count(domain)
            return count >= self.threshold
        
        elif self.alert_type == 'new_ip':
            # Check if this IP was seen before
            existing = self.env['audit.trail.log'].sudo().search([
                ('ip_address', '=', log.ip_address),
                ('user_id', '=', log.user_id.id),
                ('create_date', '<', time_limit),
            ], limit=1)
            return not existing and log.ip_address
        
        elif self.alert_type == 'off_hours':
            hour = datetime.now().hour
            return hour < 6 or hour > 22
        
        elif self.alert_type == 'rights_change':
            return log.action_type == 'rights_change'
        
        elif self.alert_type == 'invoice_delete':
            return log.action_type == 'delete' and 'account.move' in (log.model_name or '')
        
        elif self.alert_type == 'payment_cancel':
            return log.action_type == 'update' and 'account.payment' in (log.model_name or '') and log.field_name == 'state'
        
        elif self.alert_type == 'failed_login':
            return log.action_type == 'login_failed'
        
        elif self.alert_type == 'custom':
            # Custom rules can be implemented here
            return False
        
        return False

    def _trigger_alert(self, log):
        """Trigger the alert and send notifications."""
        self.ensure_one()
        
        self.write({
            'state': 'triggered',
            'last_triggered': datetime.now(),
            'trigger_count': self.trigger_count + 1,
        })
        
        # Send email notifications
        if self.notify_email and (self.notify_users or self.email_partner_ids):
            self._send_alert_email(log)
        
        # Create activity for managers
        self._create_alert_activity(log)
        
        _logger.warning(f"Audit Trail Alert Triggered: {self.name} - {log.display_name}")

    def _send_alert_email(self, log):
        """Send alert email to configured users."""
        template = self.env.ref('audit_trail_pro.email_template_audit_alert', raise_if_not_found=False)
        if not template:
            return
        
        partners = self.email_partner_ids
        if self.notify_users:
            partners |= self.notify_users.mapped('partner_id')
        
        for partner in partners:
            try:
                template.sudo().send_mail(
                    self.id,
                    partner_id=partner.id,
                    force_send=True,
                    notif_layout='audit_trail_pro.mail_notification_alert',
                )
            except Exception as e:
                _logger.error(f"Audit Trail Alert: Failed to send email to {partner.email}: {e}")

    def _create_alert_activity(self, log):
        """Create activity for alert notification."""
        self.ensure_one()
        for user in self.notify_users:
            self.activity_create(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary=f"Audit Alert: {self.name}",
                note=f"Alert triggered: {self.name}\n\nLog: {log.display_name}\n\nDetails: {log.notes or 'No additional details'}",
                user_id=user.id,
            )

    @api.model
    def _cron_check_failed_logins(self):
        """Cron to check for multiple failed login attempts."""
        config = self.env['audit.trail.config'].sudo().get_config()
        if not config:
            return
        
        time_limit = datetime.now() - timedelta(minutes=30)
        
        # Group failed logins by IP
        failed_logins = self.env['audit.trail.log'].sudo().read_group([
            ('action_type', '=', 'login_failed'),
            ('create_date', '>=', time_limit),
        ], ['ip_address'], ['ip_address'])
        
        for group in failed_logins:
            if group['ip_address_count'] >= 5:  # 5 failed attempts in 30 minutes
                alert = self.search([
                    ('alert_type', '=', 'failed_login'),
                    ('state', '=', 'active'),
                ], limit=1)
                if alert:
                    alert.write({
                        'state': 'triggered',
                        'last_triggered': datetime.now(),
                        'trigger_count': alert.trigger_count + 1,
                    })
                    _logger.warning(f"Audit Trail Alert: Multiple failed logins from IP {group['ip_address']}")
