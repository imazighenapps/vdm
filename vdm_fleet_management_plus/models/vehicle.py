# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle.plus'
    _description = 'Fleet Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Vehicle Name', required=True, tracking=True)
    license_plate = fields.Char(string='License Plate', required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Odoo Fleet Vehicle', tracking=True)
    driver_id = fields.Many2one('hr.employee', string='Current Driver', tracking=True)
    vehicle_type = fields.Selection([
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('trailer', 'Trailer'),
    ], string='Vehicle Type', required=True, tracking=True)
    make = fields.Char(string='Make', tracking=True)
    model = fields.Char(string='Model', tracking=True)
    year = fields.Integer(string='Year', tracking=True)
    color = fields.Char(string='Color', tracking=True)
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
    ], string='Fuel Type', default='diesel', tracking=True)
    odometer = fields.Float(string='Current Odometer (km)', tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', tracking=True)
    image_128 = fields.Image(string='Vehicle Image', max_size=128)
    image_256 = fields.Image(string='Vehicle Image', max_size=256)
    notes = fields.Text(string='Notes', tracking=True)
    maintenance_ids = fields.One2many('fleet.maintenance', 'vehicle_id', string='Maintenance Records')
    fuel_ids = fields.One2many('fleet.fuel', 'vehicle_id', string='Fuel Records')
    insurance_ids = fields.One2many('fleet.insurance', 'vehicle_id', string='Insurance Records')
    cost_ids = fields.One2many('fleet.cost', 'vehicle_id', string='Cost Records')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    next_maintenance_date = fields.Date(string='Next Maintenance', compute='_compute_next_maintenance', store=True)
    insurance_expiry = fields.Date(string='Insurance Expiry', compute='_compute_insurance_expiry', store=True)

    @api.depends('cost_ids.amount')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.cost_ids.mapped('amount'))

    @api.depends('maintenance_ids.next_date')
    def _compute_next_maintenance(self):
        for rec in self:
            maintenance = rec.maintenance_ids.filtered(lambda m: m.state == 'planned').sorted('next_date')
            rec.next_maintenance_date = maintenance[0].next_date if maintenance else False

    @api.depends('insurance_ids.end_date')
    def _compute_insurance_expiry(self):
        for rec in self:
            insurance = rec.insurance_ids.filtered(lambda i: i.state == 'active').sorted('end_date')
            rec.insurance_expiry = insurance[0].end_date if insurance else False

    @api.constrains('license_plate')
    def _check_license_plate(self):
        for rec in self:
            if self.search_count([('license_plate', '=', rec.license_plate), ('id', '!=', rec.id)]):
                raise ValidationError(_('License plate must be unique.'))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_deactivate(self):
        self.write({'state': 'inactive'})
