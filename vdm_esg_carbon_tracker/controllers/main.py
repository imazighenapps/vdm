from odoo import http
from odoo.http import request


class ESGDashboardController(http.Controller):

    @http.route('/esg/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        company = request.env.company
        
        inventories = request.env['esg.carbon.inventory'].search([
            ('company_id', '=', company.id),
            ('state', '=', 'posted'),
        ], order='period_end desc')
        
        latest = inventories[0] if inventories else None
        previous = inventories[1] if len(inventories) > 1 else None
        
        emission_lines = request.env['esg.emission.line'].search([
            ('company_id', '=', company.id),
            ('state', 'in', ['validated', 'approved']),
        ])
        
        scope1_lines = emission_lines.filtered(lambda l: l.scope == '1')
        scope2_lines = emission_lines.filtered(lambda l: l.scope == '2')
        scope3_lines = emission_lines.filtered(lambda l: l.scope == '3')
        
        category_data = {}
        for line in emission_lines:
            cat = line.category
            if cat not in category_data:
                category_data[cat] = 0.0
            category_data[cat] += line.emissions_tco2e
        
        targets = request.env['esg.reduction.target'].search([
            ('company_id', '=', company.id),
            ('status', '=', 'active'),
        ])
        
        offsets = request.env['esg.carbon.offset'].search([
            ('company_id', '=', company.id),
            ('state', 'in', ['purchased', 'partially_retired']),
        ])
        
        total_offsets = sum(offsets.mapped('available_credits'))
        
        yoy_change = 0.0
        if latest and previous and previous.total_emissions > 0:
            yoy_change = ((latest.total_emissions - previous.total_emissions) 
                / previous.total_emissions) * 100.0
        
        trend_data = []
        for inv in inventories[:12]:
            trend_data.append({
                'period': inv.period_end.strftime('%Y-%m') if inv.period_end else '',
                'scope1': inv.scope1_total,
                'scope2': inv.scope2_total,
                'scope3': inv.scope3_total,
                'total': inv.total_emissions,
            })
        
        return {
            'summary': {
                'total_emissions': latest.total_emissions if latest else 0.0,
                'scope1': latest.scope1_total if latest else 0.0,
                'scope2': latest.scope2_total if latest else 0.0,
                'scope3': latest.scope3_total if latest else 0.0,
                'intensity_revenue': latest.intensity_per_revenue if latest else 0.0,
                'intensity_employee': latest.intensity_per_employee if latest else 0.0,
                'reduction_vs_base': latest.reduction_vs_base if latest else 0.0,
                'yoy_change': yoy_change,
                'total_offsets': total_offsets,
                'net_emissions': (latest.total_emissions if latest else 0.0) - total_offsets,
            },
            'category_data': category_data,
            'targets': [{
                'name': t.name,
                'scope': t.scope,
                'target_year': t.target_year,
                'progress': t.progress_percentage,
                'reduction_pct': t.reduction_percentage,
            } for t in targets],
            'trend_data': trend_data,
            'anomalies': [{
                'name': inv.name,
                'period': inv.period_end.strftime('%Y-%m') if inv.period_end else '',
                'notes': inv.anomaly_notes or '',
            } for inv in inventories.filtered('anomaly_flag')[:5]],
        }
