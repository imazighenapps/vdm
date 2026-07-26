# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CostLine(models.Model):
    _name = 'construction.cost.line'
    _description = 'Cost Line'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Description', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, tracking=True)
    phase_id = fields.Many2one('construction.project.phase', string='Phase', tracking=True)
    cost_type = fields.Selection([
        ('labor', 'Labor'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('subcontract', 'Subcontract'),
        ('overhead', 'Overhead'),
        ('other', 'Other'),
    ], string='Cost Type', required=True, tracking=True)
    amount = fields.Float(string='Amount', required=True, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Vendor/Supplier', tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    time_entry_id = fields.Many2one('construction.time.entry', string='Related Time Entry', tracking=True)
