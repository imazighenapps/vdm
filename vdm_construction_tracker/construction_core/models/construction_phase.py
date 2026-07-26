# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionPhase(models.Model):
    _name = 'construction.phase'
    _description = 'Construction Phase'
    _order = 'sequence, id'

    name = fields.Char(
        string='Phase Name',
        required=True,
    )
    sequence = fields.Integer(default=10)
    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    work_type = fields.Selection([
        ('civil', 'Civil Works'),
        ('structural', 'Structural'),
        ('electrical', 'Electrical'),
        ('mep', 'MEP (Mechanical, Electrical, Plumbing)'),
        ('finishing', 'Finishing'),
        ('external', 'External Works'),
        ('foundation', 'Foundation'),
        ('roofing', 'Roofing'),
        ('landscaping', 'Landscaping'),
        ('other', 'Other'),
    ], string='Work Type', required=True, default='civil')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    weight = fields.Float(
        string='Weight (%)',
        default=1.0,
        help='Weight of this phase in overall project progress calculation',
    )
    progress = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ], string='Status', default='draft', tracking=True)
    description = fields.Text(string='Description')
    boq_line_ids = fields.One2many(
        'construction.boq.line',
        'phase_id',
        string='BOQ Lines',
    )
    work_order_ids = fields.One2many(
        'construction.work.order',
        'phase_id',
        string='Work Orders',
    )
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )
    budget_amount = fields.Monetary(
        string='Budget',
        currency_field='currency_id',
    )
    actual_cost = fields.Monetary(
        string='Actual Cost',
        compute='_compute_actual_cost',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='project_id.currency_id',
    )

    @api.depends('work_order_ids.state', 'work_order_ids.actual_cost')
    def _compute_actual_cost(self):
        for phase in self:
            done_orders = phase.work_order_ids.filtered(
                lambda o: o.state in ('done', 'in_progress')
            )
            phase.actual_cost = sum(done_orders.mapped('actual_cost'))

    @api.depends('work_order_ids.state', 'work_order_ids.progress')
    def _compute_progress(self):
        for phase in self:
            if phase.work_order_ids:
                done_count = len(phase.work_order_ids.filtered(
                    lambda o: o.state == 'done'
                ))
                total_count = len(phase.work_order_ids)
                if total_count > 0:
                    phase.progress = (done_count / total_count) * 100.0
                else:
                    phase.progress = 0.0
            else:
                phase.progress = 0.0

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed', 'progress': 100.0})

    def action_hold(self):
        self.write({'state': 'on_hold'})

    def action_draft(self):
        self.write({'state': 'draft'})
