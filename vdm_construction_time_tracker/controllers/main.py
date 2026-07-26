# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class ConstructionTimeDashboard(http.Controller):
    @http.route('/construction/time/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        # Get total hours and cost
        entries = request.env['construction.time.entry'].search([])
        total_hours = sum(entries.mapped('duration'))
        total_cost = sum(entries.mapped('total_cost'))
        
        # Get pending and approved entries
        pending_entries = request.env['construction.time.entry'].search_count([('state', '=', 'draft')])
        approved_entries = request.env['construction.time.entry'].search_count([('state', '=', 'approved')])
        
        # Get recent entries
        recent_entries = request.env['construction.time.entry'].search([], limit=10, order='entry_date desc')
        recent_entries_data = []
        for entry in recent_entries:
            recent_entries_data.append({
                'id': entry.id,
                'name': entry.name,
                'project': entry.project_id.name,
                'phase': entry.phase_id.name if entry.phase_id else '',
                'worker': entry.worker_id.name,
                'date': entry.entry_date.strftime('%Y-%m-%d') if entry.entry_date else '',
                'duration': entry.duration,
                'total_cost': entry.total_cost,
                'state': entry.state,
            })
        
        # Get projects with time entries
        projects = request.env['project.project'].search([
            ('id', 'in', entries.mapped('project_id').ids)
        ])
        projects_data = []
        for project in projects:
            project_entries = entries.filtered(lambda e: e.project_id.id == project.id)
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'total_hours': sum(project_entries.mapped('duration')),
                'total_cost': sum(project_entries.mapped('total_cost')),
            })
        
        # Get workers with time entries
        workers = request.env['construction.worker'].search([
            ('id', 'in', entries.mapped('worker_id').ids)
        ])
        workers_data = []
        for worker in workers:
            worker_entries = entries.filtered(lambda e: e.worker_id.id == worker.id)
            workers_data.append({
                'id': worker.id,
                'name': worker.name,
                'total_hours': sum(worker_entries.mapped('duration')),
                'total_cost': sum(worker_entries.mapped('total_cost')),
            })
        
        return {
            'total_hours': total_hours,
            'total_cost': total_cost,
            'pending_entries': pending_entries,
            'approved_entries': approved_entries,
            'recent_entries': recent_entries_data,
            'projects': projects_data,
            'workers': workers_data,
        }
