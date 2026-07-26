/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class ESGDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        
        this.state = useState({
            loading: true,
            summary: {},
            categoryData: {},
            targets: [],
            trendData: [],
            anomalies: [],
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            const data = await this.rpc("/esg/dashboard/data", {});
            this.state.summary = data.summary || {};
            this.state.categoryData = data.category_data || {};
            this.state.targets = data.targets || [];
            this.state.trendData = data.trend_data || [];
            this.state.anomalies = data.anomalies || [];
        } catch (error) {
            console.error("Failed to load ESG dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    getScopeColor(scope) {
        const colors = {
            '1': '#e74c3c',
            '2': '#f39c12',
            '3': '#3498db',
        };
        return colors[scope] || '#95a5a6';
    }

    getCategoryLabel(category) {
        const labels = {
            'stationary_combustion': 'Stationary Combustion',
            'mobile_combustion': 'Mobile Combustion',
            'process_emissions': 'Process Emissions',
            'fugitive_emissions': 'Fugitive Emissions',
            'purchased_energy': 'Purchased Energy',
            'upstream_transport': 'Upstream Transport',
            'waste': 'Waste',
            'business_travel': 'Business Travel',
            'employee_commuting': 'Employee Commuting',
            'other': 'Other',
        };
        return labels[category] || category;
    }

    navigateToInventories() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Carbon Inventories',
            res_model: 'esg.carbon.inventory',
            view_mode: 'list,form',
        });
    }

    navigateToTargets() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Reduction Targets',
            res_model: 'esg.reduction.target',
            view_mode: 'list,form',
        });
    }

    navigateToOffsets() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Carbon Offsets',
            res_model: 'esg.carbon.offset',
            view_mode: 'list,form',
        });
    }
}

ESGDashboard.template = "vdm_esg_carbon_tracker.ESGDashboard";

registry.category("actions").add("esg_dashboard", ESGDashboard);

export default ESGDashboard;
