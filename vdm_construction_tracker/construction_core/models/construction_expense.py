# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionExpense(models.Model):
    _name = 'construction.expense'
    _description = 'Construction Expense'
    _order = 'date desc, id desc'

    name = fields.Char(string='Description', required=True)
    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    phase_id = fields.Many2one(
        'construction.phase',
        string='Phase',
    )
    work_order_id = fields.Many2one(
        'construction.work.order',
        string='Work Order',
    )
    category = fields.Selection([
        ('material', 'Material'),
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('subcontract', 'Subcontract'),
        ('overhead', 'Overhead'),
        ('other', 'Other'),
    ], string='Category', required=True)
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True, copy=False)
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

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_draft(self):
        self.write({'state': 'draft'})
