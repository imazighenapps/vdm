# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    profitability_ids = fields.One2many('product.profitability', 'product_tmpl_id', string='Profitability Analysis')
    avg_profit_margin = fields.Float(string='Avg Profit Margin %', compute='_compute_avg_profit_margin', store=True)
    total_profit = fields.Float(string='Total Profit', compute='_compute_total_profit', store=True)

    @api.depends('profitability_ids.profit_margin')
    def _compute_avg_profit_margin(self):
        for rec in self:
            if rec.profitability_ids:
                rec.avg_profit_margin = sum(rec.profitability_ids.mapped('profit_margin')) / len(rec.profitability_ids)
            else:
                rec.avg_profit_margin = 0

    @api.depends('profitability_ids.gross_profit')
    def _compute_total_profit(self):
        for rec in self:
            rec.total_profit = sum(rec.profitability_ids.mapped('gross_profit'))
