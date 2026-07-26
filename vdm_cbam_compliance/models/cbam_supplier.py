# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CbamSupplier(models.Model):
    _name = 'cbam.supplier'
    _description = 'CBAM Supplier Emission Data'

    name = fields.Char(string='Supplier Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Supplier', required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    cbam_registered = fields.Boolean(string='CBAM Registered', default=False)
    cbam_registration_number = fields.Char(string='CBAM Registration Number')
    supplier_country_id = fields.Many2one('res.country', string='Country of Origin')
    actual_emission = fields.Float(string='Actual Emission (tCO2e/t)', digits=(16, 6))
    use_default_value = fields.Boolean(string='Use EU Default Value', default=True)
    default_emission = fields.Float(string='EU Default Emission (tCO2e/t)', digits=(16, 6))
    effective_emission = fields.Float(string='Effective Emission', compute='_compute_effective_emission', store=True)
    emission_data_ids = fields.One2many('cbam.emission.data', 'supplier_id', string='Emission Records')
    last_data_request = fields.Date(string='Last Data Request Date')
    data_status = fields.Selection([
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('partial', 'Partial'),
        ('default', 'Using Default'),
    ], string='Data Status', default='pending')

    @api.depends('actual_emission', 'default_emission', 'use_default_value')
    def _compute_effective_emission(self):
        for rec in self:
            if rec.use_default_value or not rec.actual_emission:
                rec.effective_emission = rec.default_emission
            else:
                rec.effective_emission = rec.actual_emission
