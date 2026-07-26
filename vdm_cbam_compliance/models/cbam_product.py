# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class CbamProduct(models.Model):
    _inherit = 'product.template'

    cbam_covered = fields.Boolean(string='CBAM Covered Product', default=False)
    cbam_sector = fields.Selection([
        ('cement', 'Cement'),
        ('steel', 'Iron & Steel'),
        ('aluminium', 'Aluminium'),
        ('fertilizer', 'Fertilizers'),
        ('electricity', 'Electricity'),
        ('hydrogen', 'Hydrogen'),
    ], string='CBAM Sector')
    hs_code = fields.Char(string='HS Code (Tariff)', help='Customs tariff code for CBAM identification')
    embedded_emission = fields.Float(string='Embedded Emission (tCO2e/t)', digits=(16, 6),
        help='Tonnes of CO2 equivalent per tonne of product')
    specific_embedded_emission = fields.Float(string='Specific Embedded Emission', digits=(16, 6))
    total_embedded_emission = fields.Float(string='Total Embedded Emission', compute='_compute_total_embedded', store=True)
    cbam_supplier_ids = fields.One2many('cbam.supplier', 'product_tmpl_id', string='CBAM Suppliers')

    @api.depends('embedded_emission')
    def _compute_total_embedded(self):
        for rec in self:
            rec.total_embedded_emission = rec.embedded_emission

    @api.constrains('cbam_covered', 'cbam_sector', 'embedded_emission')
    def _check_cbam_data(self):
        for rec in self:
            if rec.cbam_covered:
                if not rec.cbam_sector:
                    raise ValidationError(_('CBAM sector is required for covered products.'))
                if rec.embedded_emission < 0:
                    raise ValidationError(_('Embedded emission cannot be negative.'))
