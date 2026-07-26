# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class FleetCost(models.Model):
    _name = 'fleet.cost'
    _description = 'Fleet Cost'
    _inherit = ['mail.thread']
    _order = 'cost_date desc'

    name = fields.Char(string='Cost Description', required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle.plus', string='Vehicle', required=True, tracking=True)
    cost_type = fields.Selection([
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('toll', 'Toll'),
        ('parking', 'Parking'),
        ('fine', 'Fine'),
        ('other', 'Other'),
    ], string='Cost Type', required=True, tracking=True)
    cost_date = fields.Date(string='Cost Date', required=True, tracking=True)
    amount = fields.Float(string='Amount', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Vendor/Supplier', tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})
