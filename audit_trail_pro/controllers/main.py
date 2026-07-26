# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AuditTrailDashboard(http.Controller):
    @http.route('/audit/trail/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """Get dashboard data for the OWL dashboard."""
        user = request.env.user
        
        # Check access
        if not user.has_group('audit_trail_pro.group_audit_user'):
            return {'error': 'Access denied'}
        
        logs = request.env['audit.trail.log'].sudo()
        
        # Date range (last 30 days)
        date_from = datetime.now() - timedelta(days=30)
        recent_logs = logs.search([('create_date', '>=', date_from)])
        
        # Total counts
        total_actions = len(recent_logs)
        creates = len(recent_logs.filtered(lambda l: l.action_type == 'create'))
        updates = len(recent_logs.filtered(lambda l: l.action_type == 'update'))
        deletes = len(recent_logs.filtered(lambda l: l.action_type == 'delete'))
        logins = len(recent_logs.filtered(lambda l: l.action_type in ('login', 'logout')))
        exports = len(recent_logs.filtered(lambda l: l.action_type == 'export'))
        prints = len(recent_logs.filtered(lambda l: l.action_type == 'print'))
        emails = len(recent_logs.filtered(lambda l: l.action_type == 'email'))
        
        # Active users (logged in last 24h)
        day_ago = datetime.now() - timedelta(hours=24)
        active_users = logs.search([
            ('action_type', '=', 'login'),
            ('create_date', '>=', day_ago),
        ]).mapped('user_id')
        active_user_count = len(set(active_users.ids))
        
        # Actions by day (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        week_logs = logs.search([('create_date', '>=', week_ago)])
        actions_by_day = {}
        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            day_count = len(week_logs.filtered(
                lambda l: l.create_date and l.create_date.strftime('%Y-%m-%d') == day
            ))
            actions_by_day[day] = day_count
        
        # Actions by user (top 10)
        user_data = logs.read_group(
            [('create_date', '>=', date_from)],
            ['user_id'],
            ['user_id'],
        )
        actions_by_user = []
        for item in user_data[:10]:
            user = request.env['res.users'].browse(item['user_id'][0])
            actions_by_user.append({
                'name': user.name,
                'count': item['user_id_count'],
            })
        
        # Actions by model (top 10)
        model_data = recent_logs.read_group(
            [],
            ['model_name'],
            ['model_name'],
        )
        actions_by_model = []
        for item in model_data[:10]:
            actions_by_model.append({
                'name': item['model_name'],
                'count': item['model_name_count'],
            })
        
        # Risk assessment
        high_risk_logs = logs.search([
            ('create_date', '>=', date_from),
            ('risk_score', '>=', 20),
        ], order='risk_score desc', limit=10)
        high_risk_data = []
        for log in high_risk_logs:
            high_risk_data.append({
                'id': log.id,
                'user': log.user_id.name,
                'action': log.action_type,
                'model': log.model_name,
                'risk_score': log.risk_score,
                'date': log.create_date.strftime('%Y-%m-%d %H:%M') if log.create_date else '',
            })
        
        # Recent alerts
        recent_alerts = request.env['audit.trail.alert'].sudo().search([
            ('state', '=', 'triggered'),
        ], order='last_triggered desc', limit=5)
        alerts_data = []
        for alert in recent_alerts:
            alerts_data.append({
                'id': alert.id,
                'name': alert.name,
                'type': alert.alert_type,
                'severity': alert.severity,
                'last_triggered': alert.last_triggered.strftime('%Y-%m-%d %H:%M') if alert.last_triggered else '',
            })
        
        return {
            'total_actions': total_actions,
            'creates': creates,
            'updates': updates,
            'deletes': deletes,
            'logins': logins,
            'exports': exports,
            'prints': prints,
            'emails': emails,
            'active_users': active_user_count,
            'actions_by_day': actions_by_day,
            'actions_by_user': actions_by_user,
            'actions_by_model': actions_by_model,
            'high_risk_users': high_risk_data,
            'recent_alerts': alerts_data,
        }

    @http.route('/audit/trail/log/<int:log_id>', type='json', auth='user')
    def get_log_details(self, log_id, **kwargs):
        """Get detailed log information."""
        log = request.env['audit.trail.log'].sudo().browse(log_id)
        if not log.exists():
            return {'error': 'Log not found'}
        
        return {
            'id': log.id,
            'name': log.name,
            'user': log.user_id.name,
            'action_type': log.action_type,
            'model_name': log.model_name,
            'record_id': log.record_id,
            'record_name': log.record_name,
            'field_name': log.field_name,
            'old_value': log.old_value,
            'new_value': log.new_value,
            'ip_address': log.ip_address,
            'browser': log.browser,
            'severity': log.severity,
            'risk_score': log.risk_score,
            'date': log.create_date.strftime('%Y-%m-%d %H:%M:%S') if log.create_date else '',
        }
