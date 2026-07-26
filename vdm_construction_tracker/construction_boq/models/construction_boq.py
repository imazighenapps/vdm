# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionBoq(models.Model):
    _name = 'construction.boq'
    _description = 'Bill of Quantities'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    name = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    sequence = fields.Integer(default=10)
    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    revision = fields.Integer(string='Revision', default=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('revised', 'Revised'),
    ], string='Status', default='draft', tracking=True, copy=False)
    line_ids = fields.One2many(
        'construction.boq.line',
        'boq_id',
        string='BOQ Lines',
    )
    total_amount = fields.Monetary(
        string='Total Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_approved = fields.Monetary(
        string='Approved Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='project_id.currency_id',
    )
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('construction.boq') or 'New'
        return super().create(vals_list)

    @api.depends('line_ids.amount', 'line_ids.quantity', 'line_ids.unit_rate')
    def _compute_totals(self):
        for boq in self:
            boq.total_amount = sum(boq.line_ids.mapped('amount'))
            boq.total_approved = sum(
                line.amount for line in boq.line_ids
                if line.state == 'approved'
            )

    def action_approve(self):
        self.write({'state': 'approved'})
        self.line_ids.write({'state': 'approved'})

    def action_revise(self):
        self.write({'state': 'revised', 'revision': self.revision + 1})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_copy_from_project(self):
        """Copy BOQ lines from approved BOQ"""
        self.ensure_one()
        approved_boq = self.env['construction.boq'].search([
            ('project_id', '=', self.project_id.id),
            ('state', '=', 'approved'),
            ('id', '!=', self.id),
        ], limit=1)
        if approved_boq:
            for line in approved_boq.line_ids:
                line.copy({'boq_id': self.id})
