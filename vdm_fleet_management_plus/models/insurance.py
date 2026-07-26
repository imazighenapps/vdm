# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class FleetInsurance(models.Model):
    _name = 'fleet.insurance'
    _description = 'Fleet Insurance'
    _inherit = ['mail.thread']
    _order = 'start_date desc'

    name = fields.Char(string='Insurance Description', required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle.plus', string='Vehicle', required=True, tracking=True)
    insurance_type = fields.Selection([
        ('comprehensive', 'Comprehensive'),
        ('third_party', 'Third Party'),
        ('collision', 'Collision'),
        ('liability', 'Liability'),
    ], string='Insurance Type', required=True, tracking=True)
    provider_id = fields.Many2one('res.partner', string='Insurance Provider', tracking=True)
    policy_number = fields.Char(string='Policy Number', tracking=True)
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    premium = fields.Float(string='Annual Premium', tracking=True)
    coverage_amount = fields.Float(string='Coverage Amount', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    def action_activate(self):
        self.write({'state': 'active'})

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})
