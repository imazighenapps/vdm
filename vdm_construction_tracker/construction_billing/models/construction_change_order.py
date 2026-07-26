# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionChangeOrder(models.Model):
    _name = 'construction.change.order'
    _description = 'Change Order'
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
    description = fields.Text(string='Description', required=True)
    reason = fields.Selection([
        ('client_request', 'Client Request'),
        ('design_change', 'Design Change'),
        ('site_condition', 'Site Condition'),
        ('regulation', 'Regulation Change'),
        ('error', 'Error in Original'),
        ('other', 'Other'),
    ], string='Reason', required=True)
    original_amount = fields.Monetary(
        string='Original Amount',
        currency_field='currency_id',
    )
    variation_amount = fields.Monetary(
        string='Variation Amount',
        currency_field='currency_id',
    )
    new_total = fields.Monetary(
        string='New Total',
        compute='_compute_new_total',
        store=True,
        currency_field='currency_id',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ], string='Status', default='draft', tracking=True, copy=False)
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
    )
    approval_date = fields.Datetime(string='Approval Date', readonly=True)
    implementation_date = fields.Date(string='Implementation Date')
    currency_id = fields.Many2one(
        'res.currency',
        related='project_id.currency_id',
    )
    boq_line_id = fields.Many2one(
        'construction.boq.line',
        string='Related BOQ Line',
    )
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )
    notes = fields.Text(string='Internal Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('construction.change.order') or 'New'
        return super().create(vals_list)

    @api.depends('original_amount', 'variation_amount')
    def _compute_new_total(self):
        for order in self:
            order.new_total = order.original_amount + order.variation_amount

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_implement(self):
        self.write({'state': 'implemented'})

    def action_draft(self):
        self.write({'state': 'draft'})
