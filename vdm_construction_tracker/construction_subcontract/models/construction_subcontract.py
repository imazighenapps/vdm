# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionSubcontract(models.Model):
    _name = 'construction.subcontract'
    _description = 'Subcontract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
    )
    sequence = fields.Integer(default=10)
    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Subcontractor',
        required=True,
    )
    scope_of_work = fields.Text(string='Scope of Work')
    contract_value = fields.Monetary(
        string='Contract Value',
        currency_field='currency_id',
    )
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    retention_pct = fields.Float(
        string='Retention (%)',
        default=5.0,
    )
    retention_amount = fields.Monetary(
        string='Retention Amount',
        compute='_compute_retention',
        store=True,
        currency_field='currency_id',
    )
    amount_paid = fields.Monetary(
        string='Amount Paid',
        default=0.0,
        currency_field='currency_id',
    )
    amount_remaining = fields.Monetary(
        string='Remaining Amount',
        compute='_compute_remaining',
        store=True,
        currency_field='currency_id',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('settled', 'Settled'),
    ], string='Status', default='draft', tracking=True, copy=False)
    phase_id = fields.Many2one(
        'construction.phase',
        string='Phase',
    )
    measurement_ids = fields.One2many(
        'construction.subcontract.measurement',
        'subcontract_id',
        string='Measurements',
    )
    total_measured = fields.Monetary(
        string='Total Measured',
        compute='_compute_total_measured',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='project_id.currency_id',
    )
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )
    notes = fields.Text(string='Notes')

    @api.depends('contract_value', 'retention_pct')
    def _compute_retention(self):
        for sub in self:
            sub.retention_amount = sub.contract_value * (sub.retention_pct / 100.0)

    @api.depends('contract_value', 'retention_amount', 'amount_paid')
    def _compute_remaining(self):
        for sub in self:
            sub.amount_remaining = (
                sub.contract_value - sub.retention_amount - sub.amount_paid
            )

    @api.depends('measurement_ids.amount')
    def _compute_total_measured(self):
        for sub in self:
            sub.total_measured = sum(sub.measurement_ids.mapped('amount'))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_settle(self):
        self.write({'state': 'settled'})

    def action_draft(self):
        self.write({'state': 'draft'})


class ConstructionSubcontractMeasurement(models.Model):
    _name = 'construction.subcontract.measurement'
    _description = 'Subcontractor Measurement'
    _order = 'date desc, id'

    name = fields.Char(string='Description')
    subcontract_id = fields.Many2one(
        'construction.subcontract',
        string='Subcontract',
        required=True,
        ondelete='cascade',
    )
    project_id = fields.Many2one(
        'construction.project',
        related='subcontract_id.project_id',
        store=True,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
    )
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    rate = fields.Monetary(
        string='Rate',
        currency_field='currency_id',
    )
    amount = fields.Monetary(
        string='Amount',
        compute='_compute_amount',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='subcontract_id.currency_id',
    )
    measured_by = fields.Many2one(
        'res.users',
        string='Measured By',
        default=lambda self: self.env.user,
    )

    @api.depends('quantity', 'rate')
    def _compute_amount(self):
        for m in self:
            m.amount = m.quantity * m.rate
