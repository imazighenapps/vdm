# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionRaBilling(models.Model):
    _name = 'construction.ra.billing'
    _description = 'Running Account Billing'
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
    period = fields.Char(string='Billing Period')
    billing_date = fields.Date(
        string='Billing Date',
        default=fields.Date.context_today,
    )
    bill_line_ids = fields.One2many(
        'construction.ra.billing.line',
        'billing_id',
        string='Billing Lines',
    )
    total_amount = fields.Monetary(
        string='Total Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    retention_pct = fields.Float(
        string='Retention (%)',
        default=5.0,
    )
    retention_amount = fields.Monetary(
        string='Retention Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    advance_recovery = fields.Monetary(
        string='Advance Recovery',
        currency_field='currency_id',
    )
    net_payable = fields.Monetary(
        string='Net Payable',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ], string='Status', default='draft', tracking=True, copy=False)
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True,
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
    previous_bill_amount = fields.Monetary(
        string='Previous Bill Amount',
        currency_field='currency_id',
    )
    cumulative_amount = fields.Monetary(
        string='Cumulative Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('construction.ra.billing') or 'New'
        return super().create(vals_list)

    @api.depends('bill_line_ids.amount', 'previous_bill_amount', 'retention_pct', 'advance_recovery')
    def _compute_totals(self):
        for billing in self:
            total = sum(billing.bill_line_ids.mapped('amount'))
            billing.total_amount = total
            billing.retention_amount = total * (billing.retention_pct / 100.0)
            billing.cumulative_amount = billing.previous_bill_amount + total
            billing.net_payable = (
                total
                - billing.retention_amount
                - billing.advance_recovery
            )

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_pay(self):
        self.write({'state': 'paid'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_create_invoice(self):
        self.ensure_one()
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.project_id.client_id.id,
            'invoice_date': self.billing_date,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.unit_rate,
                })
                for line in self.bill_line_ids
            ],
        })
        self.write({'invoice_id': invoice.id})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
