/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ProductProfitabilityDashboard extends Component {
    setup() {
        this.state = useState({
            totalAnalyses: 0,
            computedAnalyses: 0,
            totalSales: 0,
            totalProfit: 0,
            avgMargin: 0,
            topProducts: [],
            recentAnalyses: [],
        });
        
        this.rpc = useService("rpc");
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }
    
    async loadDashboardData() {
        const data = await this.rpc("/product/profitability/dashboard/data", {});
        this.state.totalAnalyses = data.total_analyses || 0;
        this.state.computedAnalyses = data.computed_analyses || 0;
        this.state.totalSales = data.total_sales || 0;
        this.state.totalProfit = data.total_profit || 0;
        this.state.avgMargin = data.avg_margin || 0;
        this.state.topProducts = data.top_products || [];
        this.state.recentAnalyses = data.recent_analyses || [];
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }
    
    formatPercent(value) {
        return `${value.toFixed(1)}%`;
    }
}

ProductProfitabilityDashboard.template = "vdm_product_profitability.ProductProfitabilityDashboard";

registry.category("actions").add("product_profitability_dashboard", ProductProfitabilityDashboard);
