# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CbamEmissionData(models.Model):
    _name = 'cbam.emission.data'
    _description = 'CBAM Emission Data Record'
    _order = 'date desc'

    name = fields.Char(string='Reference')
    supplier_id = fields.Many2one('cbam.supplier', string='Supplier', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    quantity = fields.Float(string='Quantity (tonnes)', digits=(16, 4))
    emission_value = fields.Float(string='Emission Value (tCO2e/t)', digits=(16, 6))
    total_emission = fields.Float(string='Total Emission (tCO2e)', compute='_compute_total', store=True, digits=(16, 4))
    source = fields.Selection([
        ('supplier', 'Supplier Data'),
        ('default', 'EU Default'),
        ('calculated', 'Calculated'),
    ], string='Source', default='supplier')
    verified = fields.Boolean(string='Verified', default=False)
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'emission_value')
    def _compute_total(self):
        for rec in self:
            rec.total_emission = rec.quantity * rec.emission_value
