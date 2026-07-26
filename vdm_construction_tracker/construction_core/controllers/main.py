# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ConstructionDashboard(http.Controller):

    @http.route('/construction/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """Return dashboard data for the OWL widget."""
        Project = request.env['construction.project']
        Diary = request.env['construction.site.diary']
        ChangeOrder = request.env['construction.change.order']

        # Stats
        all_projects = Project.search([])
        active_projects = all_projects.filtered(lambda p: p.state == 'in_progress')

        total_value = sum(all_projects.mapped('contract_value'))
        avg_progress = 0.0
        if active_projects:
            avg_progress = sum(active_projects.mapped('progress')) / len(active_projects)

        # Projects list
        projects_data = []
        for project in all_projects[:20]:
            projects_data.append({
                'id': project.id,
                'reference': project.reference or '',
                'name': project.name or '',
                'client': project.client_id.name if project.client_id else '',
                'contract_value': project.contract_value or 0,
                'progress': round(project.progress, 1),
                'state': project.state or 'draft',
            })

        # Alerts
        alerts = []
        overdue_projects = all_projects.filtered(
            lambda p: p.end_date and p.end_date < request.env.context.get('today') and p.state == 'in_progress'
        )
        for project in overdue_projects:
            alerts.append({
                'type': 'danger',
                'message': 'Project "%s" is past its end date!' % project.name,
            })

        urgent_cos = ChangeOrder.search([
            ('state', '=', 'submitted'),
            ('reason', '=', 'client_request'),
        ], limit=5)
        for co in urgent_cos:
            alerts.append({
                'type': 'warning',
                'message': 'Change Order "%s" is pending approval.' % co.name,
            })

        return {
            'stats': {
                'total_projects': len(all_projects),
                'active_projects': len(active_projects),
                'total_value': total_value,
                'avg_progress': round(avg_progress, 1),
            },
            'projects': projects_data,
            'alerts': alerts,
        }
