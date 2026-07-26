# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionWorkOrder(models.Model):
    _name = 'construction.work.order'
    _description = 'Construction Work Order'
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
    phase_id = fields.Many2one(
        'construction.phase',
        string='Phase',
        required=True,
    )
    boq_line_id = fields.Many2one(
        'construction.boq.line',
        string='BOQ Line',
    )
    foreman_id = fields.Many2one(
        'hr.employee',
        string='Foreman',
    )
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)
    planned_start = fields.Datetime(string='Planned Start')
    planned_end = fields.Datetime(string='Planned End')
    actual_start = fields.Datetime(string='Actual Start')
    actual_end = fields.Datetime(string='Actual End')
    planned_cost = fields.Monetary(
        string='Planned Cost',
        currency_field='currency_id',
    )
    actual_cost = fields.Monetary(
        string='Actual Cost',
        currency_field='currency_id',
    )
    progress = fields.Float(string='Progress (%)')
    description = fields.Text(string='Description')
    currency_id = fields.Many2one(
        'res.currency',
        related='project_id.currency_id',
    )
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('construction.work.order') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({
            'state': 'in_progress',
            'actual_start': fields.Datetime.now(),
        })

    def action_done(self):
        self.write({
            'state': 'done',
            'actual_end': fields.Datetime.now(),
            'progress': 100.0,
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})
