# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class FleetManagementDashboard(http.Controller):
    @http.route('/fleet/management/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        # Get all vehicles
        vehicles = request.env['fleet.vehicle.plus'].search([])
        
        # Get statistics
        total_vehicles = len(vehicles)
        active_vehicles = len(vehicles.filtered(lambda v: v.state == 'active'))
        maintenance_vehicles = len(vehicles.filtered(lambda v: v.state == 'maintenance'))
        inactive_vehicles = len(vehicles.filtered(lambda v: v.state == 'inactive'))
        
        # Get costs
        total_cost = sum(vehicles.mapped('total_cost'))
        
        # Get recent maintenance
        recent_maintenance = request.env['fleet.maintenance'].search([], limit=5, order='maintenance_date desc')
        maintenance_data = []
        for m in recent_maintenance:
            maintenance_data.append({
                'id': m.id,
                'vehicle': m.vehicle_id.name,
                'name': m.name,
                'date': m.maintenance_date.strftime('%Y-%m-%d') if m.maintenance_date else '',
                'cost': m.cost,
                'state': m.state,
            })
        
        # Get recent fuel entries
        recent_fuel = request.env['fleet.fuel'].search([], limit=5, order='fuel_date desc')
        fuel_data = []
        for f in recent_fuel:
            fuel_data.append({
                'id': f.id,
                'vehicle': f.vehicle_id.name,
                'date': f.fuel_date.strftime('%Y-%m-%d') if f.fuel_date else '',
                'liters': f.liters,
                'total_cost': f.total_cost,
            })
        
        # Get upcoming insurance expirations
        upcoming_insurance = request.env['fleet.insurance'].search([
            ('state', '=', 'active'),
        ], limit=5, order='end_date asc')
        insurance_data = []
        for i in upcoming_insurance:
            insurance_data.append({
                'id': i.id,
                'vehicle': i.vehicle_id.name,
                'end_date': i.end_date.strftime('%Y-%m-%d') if i.end_date else '',
                'premium': i.premium,
            })
        
        return {
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'maintenance_vehicles': maintenance_vehicles,
            'inactive_vehicles': inactive_vehicles,
            'total_cost': total_cost,
            'recent_maintenance': maintenance_data,
            'recent_fuel': fuel_data,
            'upcoming_insurance': insurance_data,
        }
