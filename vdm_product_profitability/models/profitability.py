# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProfitability(models.Model):
    _name = 'product.profitability'
    _description = 'Product Profitability'
    _inherit = ['mail.thread']
    _order = 'profit_margin desc'

    name = fields.Char(string='Profitability Analysis', required=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, tracking=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', related='product_id.product_tmpl_id', store=True)
    categ_id = fields.Many2one('product.category', string='Category', related='product_id.categ_id', store=True)
    date_from = fields.Date(string='From Date', required=True, tracking=True)
    date_to = fields.Date(string='To Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
    ], string='Status', default='draft', tracking=True)
    
    # Sales Data
    total_sales = fields.Float(string='Total Sales', compute='_compute_profitability', store=True)
    total_quantity = fields.Float(string='Total Quantity Sold', compute='_compute_profitability', store=True)
    avg_selling_price = fields.Float(string='Avg Selling Price', compute='_compute_profitability', store=True)
    
    # Cost Data
    total_cost = fields.Float(string='Total Cost', compute='_compute_profitability', store=True)
    cost_per_unit = fields.Float(string='Cost per Unit', compute='_compute_profitability', store=True)
    
    # Profit Data
    gross_profit = fields.Float(string='Gross Profit', compute='_compute_profitability', store=True)
    profit_margin = fields.Float(string='Profit Margin %', compute='_compute_profitability', store=True)
    profit_per_unit = fields.Float(string='Profit per Unit', compute='_compute_profitability', store=True)
    
    # Detailed Lines
    line_ids = fields.One2many('product.profitability.line', 'profitability_id', string='Profitability Lines')
    
    # Notes
    notes = fields.Text(string='Notes', tracking=True)

    @api.depends('product_id', 'date_from', 'date_to', 'line_ids')
    def _compute_profitability(self):
        for rec in self:
            if rec.product_id and rec.date_from and rec.date_to:
                # Get sale lines
                sale_lines = self.env['sale.order.line'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('order_id.date_order', '>=', rec.date_from),
                    ('order_id.date_order', '<=', rec.date_to),
                    ('order_id.state', 'in', ['sale', 'done']),
                ])
                
                # Get invoice lines
                invoice_lines = self.env['account.move.line'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('move_id.invoice_date', '>=', rec.date_from),
                    ('move_id.invoice_date', '<=', rec.date_to),
                    ('move_id.state', '=', 'posted'),
                    ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
                ])
                
                # Calculate sales
                rec.total_sales = sum(invoice_lines.mapped('price_subtotal'))
                rec.total_quantity = sum(invoice_lines.mapped('quantity'))
                rec.avg_selling_price = rec.total_sales / rec.total_quantity if rec.total_quantity else 0
                
                # Calculate cost
                rec.total_cost = sum(invoice_lines.mapped(lambda l: l.quantity * l.product_id.standard_price))
                rec.cost_per_unit = rec.total_cost / rec.total_quantity if rec.total_quantity else 0
                
                # Calculate profit
                rec.gross_profit = rec.total_sales - rec.total_cost
                rec.profit_margin = (rec.gross_profit / rec.total_sales * 100) if rec.total_sales else 0
                rec.profit_per_unit = rec.gross_profit / rec.total_quantity if rec.total_quantity else 0
                
                rec.state = 'computed'
            else:
                rec.total_sales = 0
                rec.total_quantity = 0
                rec.avg_selling_price = 0
                rec.total_cost = 0
                rec.cost_per_unit = 0
                rec.gross_profit = 0
                rec.profit_margin = 0
                rec.profit_per_unit = 0

    def action_compute(self):
        for rec in self:
            rec._compute_profitability()

    def action_view_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales'),
            'res_model': 'account.move.line',
            'view_mode': 'list,form',
            'domain': [
                ('product_id', '=', self.product_id.id),
                ('move_id.invoice_date', '>=', self.date_from),
                ('move_id.invoice_date', '<=', self.date_to),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
            ],
        }


class ProductProfitabilityLine(models.Model):
    _name = 'product.profitability.line'
    _description = 'Product Profitability Line'

    profitability_id = fields.Many2one('product.profitability', string='Profitability Analysis', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    date = fields.Date(string='Date', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    unit_price = fields.Float(string='Unit Price', required=True)
    total_price = fields.Float(string='Total Price', required=True)
    cost = fields.Float(string='Cost', required=True)
    profit = fields.Float(string='Profit', required=True)
    profit_margin = fields.Float(string='Profit Margin %', required=True)
