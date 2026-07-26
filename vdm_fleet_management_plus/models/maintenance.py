# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class FleetMaintenance(models.Model):
    _name = 'fleet.maintenance'
    _description = 'Fleet Maintenance'
    _inherit = ['mail.thread']
    _order = 'maintenance_date desc'

    name = fields.Char(string='Maintenance Description', required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle.plus', string='Vehicle', required=True, tracking=True)
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
    ], string='Maintenance Type', required=True, tracking=True)
    maintenance_date = fields.Date(string='Maintenance Date', required=True, tracking=True)
    next_date = fields.Date(string='Next Maintenance', tracking=True)
    odometer = fields.Float(string='Odometer at Maintenance', tracking=True)
    cost = fields.Float(string='Cost', tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Service Provider', tracking=True)
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    parts_ids = fields.One2many('fleet.maintenance.part', 'maintenance_id', string='Parts Used')

    def action_plan(self):
        self.write({'state': 'planned'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class FleetMaintenancePart(models.Model):
    _name = 'fleet.maintenance.part'
    _description = 'Maintenance Part'

    name = fields.Char(string='Part Name', required=True)
    maintenance_id = fields.Many2one('fleet.maintenance', string='Maintenance', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.quantity * rec.unit_price
