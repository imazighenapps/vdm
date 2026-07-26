# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionRaBillingLine(models.Model):
    _name = 'construction.ra.billing.line'
    _description = 'RA Billing Line'
    _order = 'sequence, id'

    name = fields.Char(string='Description', required=True)
    sequence = fields.Integer(default=10)
    billing_id = fields.Many2one(
        'construction.ra.billing',
        string='Billing',
        required=True,
        ondelete='cascade',
    )
    project_id = fields.Many2one(
        'construction.project',
        related='billing_id.project_id',
        store=True,
    )
    boq_line_id = fields.Many2one(
        'construction.boq.line',
        string='BOQ Line',
    )
    phase_id = fields.Many2one(
        'construction.phase',
        string='Phase',
    )
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_rate = fields.Monetary(
        string='Unit Rate',
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
        related='billing_id.currency_id',
    )

    @api.depends('quantity', 'unit_rate')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.unit_rate
