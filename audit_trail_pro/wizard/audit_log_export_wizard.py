# -*- coding: utf-8 -*-
import base64
import csv
import io

from odoo import models, fields, api, _


class AuditLogExportWizard(models.TransientModel):
    _name = 'audit.log.export.wizard'
    _description = 'Audit Log Export Wizard'

    name = fields.Char(string='File Name', default='audit_logs_export.csv')
    export_format = fields.Selection([
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ], string='Export Format', default='csv', required=True)
    
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    user_ids = fields.Many2many('res.users', string='Users')
    model_ids = fields.Many2many('ir.model', string='Models')
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
    ], string='Action Type')
    
    data_file = fields.Binary(string='File')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    def action_export(self):
        """Export audit logs to file."""
        domain = []
        
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        if self.user_ids:
            domain.append(('user_id', 'in', self.user_ids.ids))
        if self.model_ids:
            domain.append(('model_name', 'in', self.model_ids.mapped('model')))
        if self.action_type:
            domain.append(('action_type', '=', self.action_type))
        
        logs = self.env['audit.trail.log'].sudo().search(domain)
        
        if self.export_format == 'csv':
            return self._export_csv(logs)
        else:
            return self._export_excel(logs)

    def _export_csv(self, logs):
        """Export logs to CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Date', 'User', 'Login', 'Action', 'Model', 'Record ID',
            'Record Name', 'Field', 'Old Value', 'New Value', 'IP Address',
            'Browser', 'OS', 'Severity', 'Risk Score', 'Notes'
        ])
        
        # Data
        for log in logs:
            writer.writerow([
                log.create_date.strftime('%Y-%m-%d %H:%M:%S') if log.create_date else '',
                log.user_id.name or '',
                log.login or '',
                log.action_type or '',
                log.model_name or '',
                log.record_id or '',
                log.record_name or '',
                log.field_name or '',
                log.old_value or '',
                log.new_value or '',
                log.ip_address or '',
                log.browser or '',
                log.operating_system or '',
                log.severity or '',
                log.risk_score or 0,
                log.notes or '',
            ])
        
        # Create attachment
        data = output.getvalue().encode('utf-8')
        attachment = self.env['ir.attachment'].create({
            'name': self.name or 'audit_logs_export.csv',
            'type': 'binary',
            'datas': base64.b64encode(data),
            'mimetype': 'text/csv',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Complete',
            'res_model': 'audit.log.export.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_state': 'done', 'default_data_file': attachment.datas},
        }

    def _export_excel(self, logs):
        """Export logs to Excel (simplified CSV for now)."""
        return self._export_csv(logs)

    def action_download(self):
        """Download the exported file."""
        if self.data_file:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Download',
                'res_model': 'ir.attachment',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.env['ir.attachment'].search([('datas', '=', self.data_file)], limit=1).id,
            }
        return False
