# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionBoqLine(models.Model):
    _name = 'construction.boq.line'
    _description = 'BOQ Line'
    _order = 'sequence, id'

    name = fields.Char(
        string='Description',
        required=True,
    )
    sequence = fields.Integer(default=10)
    boq_id = fields.Many2one(
        'construction.boq',
        string='BOQ',
        required=True,
        ondelete='cascade',
    )
    project_id = fields.Many2one(
        'construction.project',
        related='boq_id.project_id',
        store=True,
    )
    phase_id = fields.Many2one(
        'construction.phase',
        string='Phase',
    )
    work_type = fields.Selection([
        ('civil', 'Civil Works'),
        ('structural', 'Structural'),
        ('electrical', 'Electrical'),
        ('mep', 'MEP'),
        ('finishing', 'Finishing'),
        ('external', 'External Works'),
        ('foundation', 'Foundation'),
        ('roofing', 'Roofing'),
        ('landscaping', 'Landscaping'),
        ('other', 'Other'),
    ], string='Work Type', default='civil')
    item_code = fields.Char(string='Item Code')
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit',
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
    quantity_done = fields.Float(
        string='Quantity Done',
        default=0.0,
    )
    quantity_invoiced = fields.Float(
        string='Quantity Invoiced',
        default=0.0,
    )
    progress = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ], string='Status', default='draft')
    currency_id = fields.Many2one(
        'res.currency',
        related='boq_id.currency_id',
    )
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_rate')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.unit_rate

    @api.depends('quantity', 'quantity_done')
    def _compute_progress(self):
        for line in self:
            if line.quantity > 0:
                line.progress = min((line.quantity_done / line.quantity) * 100.0, 100.0)
            else:
                line.progress = 0.0
