# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DailySummaryWizard(models.TransientModel):
    _name = 'daily.summary.wizard'
    _description = 'Daily Summary Wizard'

    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    project_id = fields.Many2one('project.project', string='Project')
    worker_id = fields.Many2one('construction.worker', string='Worker')

    def action_generate(self):
        domain = [('entry_date', '=', self.date)]
        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
        if self.worker_id:
            domain.append(('worker_id', '=', self.worker_id.id))

        entries = self.env['construction.time.entry'].search(domain)
        if not entries:
            raise ValidationError('No time entries found for the selected criteria.')

        return {
            'type': 'ir.actions.report',
            'report_name': 'vdm_construction_time_tracker.report_time_entry',
            'report_type': 'qweb-pdf',
            'data': {
                'docs': entries.ids,
            },
        }
