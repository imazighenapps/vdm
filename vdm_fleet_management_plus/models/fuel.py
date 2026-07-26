# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class FleetFuel(models.Model):
    _name = 'fleet.fuel'
    _description = 'Fleet Fuel'
    _inherit = ['mail.thread']
    _order = 'fuel_date desc'

    name = fields.Char(string='Fuel Entry Description', required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle.plus', string='Vehicle', required=True, tracking=True)
    driver_id = fields.Many2one('hr.employee', string='Driver', tracking=True)
    fuel_date = fields.Date(string='Fuel Date', required=True, tracking=True)
    liters = fields.Float(string='Liters', required=True, tracking=True)
    price_per_liter = fields.Float(string='Price per Liter', required=True, tracking=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    odometer = fields.Float(string='Odometer', tracking=True)
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
    ], string='Fuel Type', tracking=True)
    station = fields.Char(string='Fuel Station', tracking=True)
    receipt_number = fields.Char(string='Receipt Number', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    @api.depends('liters', 'price_per_liter')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.liters * rec.price_per_liter

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})
