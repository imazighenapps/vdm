# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    audit_risk_score = fields.Integer(string='Audit Risk Score', compute='_compute_audit_risk_score', store=True)
    audit_log_count = fields.Integer(string='Audit Log Count', compute='_compute_audit_log_count')
    last_login_ip = fields.Char(string='Last Login IP', compute='_compute_last_login')

    @api.depends('audit_log_ids')
    def _compute_audit_risk_score(self):
        for user in self:
            logs = self.env['audit.trail.log'].sudo().search([
                ('user_id', '=', user.id),
                ('risk_score', '>', 0),
            ])
            user.audit_risk_score = sum(logs.mapped('risk_score'))

    def _compute_audit_log_count(self):
        for user in self:
            user.audit_log_count = self.env['audit.trail.log'].sudo().search_count([
                ('user_id', '=', user.id),
            ])

    def _compute_last_login(self):
        for user in self:
            last_login = self.env['audit.trail.log'].sudo().search([
                ('user_id', '=', user.id),
                ('action_type', '=', 'login'),
            ], limit=1)
            user.last_login_ip = last_login.ip_address if last_login else ''

    def action_view_audit_logs(self):
        """View audit logs for this user."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Audit Logs - {self.name}',
            'res_model': 'audit.trail.log',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('user_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_risk_details(self):
        """View risk details for this user."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Risk Details - {self.name}',
            'res_model': 'audit.trail.log',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.id), ('risk_score', '>', 0)],
            'target': 'current',
        }
