# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CbamCertificate(models.Model):
    _name = 'cbam.certificate'
    _description = 'CBAM Certificate'
    _order = 'purchase_date desc'

    name = fields.Char(string='Certificate Reference', required=True, copy=False, default='New')
    purchase_date = fields.Date(string='Purchase Date', required=True)
    quantity = fields.Float(string='Quantity (certificates)', required=True, digits=(16, 2))
    price_per_unit = fields.Float(string='Price per Unit (€)', required=True, digits=(16, 2))
    total_cost = fields.Float(string='Total Cost (€)', compute='_compute_total_cost', store=True, digits=(16, 2))
    remaining_quantity = fields.Float(string='Remaining', compute='_compute_remaining', store=True, digits=(16, 2))
    surrendered_ids = fields.One2many('cbam.certificate.surrender', 'certificate_id', string='Surrenders')
    status = fields.Selection([
        ('available', 'Available'),
        ('partial', 'Partially Surrendered'),
        ('surrendered', 'Fully Surrendered'),
    ], string='Status', compute='_compute_status', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'price_per_unit')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.price_per_unit

    @api.depends('quantity', 'surrendered_ids.quantity')
    def _compute_remaining(self):
        for rec in self:
            surrendered = sum(rec.surrendered_ids.mapped('quantity'))
            rec.remaining_quantity = max(0, rec.quantity - surrendered)

    @api.depends('remaining_quantity', 'quantity')
    def _compute_status(self):
        for rec in self:
            if rec.remaining_quantity >= rec.quantity:
                rec.status = 'available'
            elif rec.remaining_quantity > 0:
                rec.status = 'partial'
            else:
                rec.status = 'surrendered'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cbam.certificate') or 'New'
        return super().create(vals_list)


class CbamCertificateSurrender(models.Model):
    _name = 'cbam.certificate.surrender'
    _description = 'CBAM Certificate Surrender'

    certificate_id = fields.Many2one('cbam.certificate', string='Certificate', required=True, ondelete='cascade')
    quarterly_report_id = fields.Many2one('cbam.quarterly.report', string='Quarterly Report')
    quantity = fields.Float(string='Quantity Surrendered', required=True, digits=(16, 2))
    surrender_date = fields.Date(string='Surrender Date', default=fields.Date.context_today)
    notes = fields.Text(string='Notes')
