# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CbamImportEvent(models.Model):
    _name = 'cbam.import.event'
    _description = 'CBAM Import Event'
    _order = 'import_date desc'

    name = fields.Char(string='Reference', required=True, copy=False, default='New')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier', required=True)
    quantity = fields.Float(string='Quantity Imported (tonnes)', required=True, digits=(16, 4))
    emission_factor = fields.Float(string='Emission Factor (tCO2e/t)', digits=(16, 6),
        compute='_compute_emission_factor', store=True)
    total_emissions = fields.Float(string='Total Emissions (tCO2e)', compute='_compute_total_emissions', store=True, digits=(16, 4))
    sector = fields.Selection([
        ('cement', 'Cement'),
        ('steel', 'Iron & Steel'),
        ('aluminium', 'Aluminium'),
        ('fertilizer', 'Fertilizers'),
        ('electricity', 'Electricity'),
        ('hydrogen', 'Hydrogen'),
    ], string='CBAM Sector', required=True)
    origin_country_id = fields.Many2one('res.country', string='Country of Origin', required=True)
    import_date = fields.Date(string='Import Date', default=fields.Date.context_today, required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft')
    quarterly_report_id = fields.Many2one('cbam.quarterly.report', string='Quarterly Report')
    geo_json_file = fields.Binary(string='GeoJSON File')
    geo_json_filename = fields.Char(string='GeoJSON Filename')
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('product_id', 'supplier_id')
    def _compute_emission_factor(self):
        for rec in self:
            if rec.product_id and rec.product_id.product_tmpl_id.cbam_covered:
                rec.emission_factor = rec.product_id.product_tmpl_id.embedded_emission
            else:
                rec.emission_factor = 0.0

    @api.depends('quantity', 'emission_factor')
    def _compute_total_emissions(self):
        for rec in self:
            rec.total_emissions = rec.quantity * rec.emission_factor

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cbam.import.event') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            rec.status = 'submitted'

    def action_confirm(self):
        for rec in self:
            rec.status = 'confirmed'

    def action_draft(self):
        for rec in self:
            rec.status = 'draft'
