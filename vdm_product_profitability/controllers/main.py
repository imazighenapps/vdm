# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ProductProfitabilityDashboard(http.Controller):
    @http.route('/product/profitability/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        # Get all profitability analyses
        analyses = request.env['product.profitability'].search([])
        
        # Get statistics
        total_analyses = len(analyses)
        computed_analyses = len(analyses.filtered(lambda a: a.state == 'computed'))
        
        # Get total sales and profit
        total_sales = sum(analyses.mapped('total_sales'))
        total_profit = sum(analyses.mapped('gross_profit'))
        avg_margin = sum(analyses.mapped('profit_margin')) / len(analyses) if analyses else 0
        
        # Get top products by margin
        top_products = analyses.sorted(lambda a: a.profit_margin, reverse=True)[:10]
        top_products_data = []
        for p in top_products:
            top_products_data.append({
                'id': p.id,
                'name': p.product_id.name,
                'sales': p.total_sales,
                'profit': p.gross_profit,
                'margin': p.profit_margin,
            })
        
        # Get recent analyses
        recent_analyses = analyses.sorted(lambda a: a.create_date, reverse=True)[:10]
        recent_data = []
        for a in recent_analyses:
            recent_data.append({
                'id': a.id,
                'name': a.name,
                'product': a.product_id.name,
                'date_from': a.date_from.strftime('%Y-%m-%d') if a.date_from else '',
                'date_to': a.date_to.strftime('%Y-%m-%d') if a.date_to else '',
                'sales': a.total_sales,
                'profit': a.gross_profit,
                'margin': a.profit_margin,
                'state': a.state,
            })
        
        return {
            'total_analyses': total_analyses,
            'computed_analyses': computed_analyses,
            'total_sales': total_sales,
            'total_profit': total_profit,
            'avg_margin': avg_margin,
            'top_products': top_products_data,
            'recent_analyses': recent_data,
        }
