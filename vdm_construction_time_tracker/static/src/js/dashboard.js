/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ConstructionTimeDashboard extends Component {
    setup() {
        this.state = useState({
            totalHours: 0,
            totalCost: 0,
            pendingEntries: 0,
            approvedEntries: 0,
            entries: [],
            projects: [],
            workers: [],
        });
        
        this.rpc = useService("rpc");
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }
    
    async loadDashboardData() {
        const data = await this.rpc("/construction/time/dashboard/data", {});
        this.state.totalHours = data.total_hours || 0;
        this.state.totalCost = data.total_cost || 0;
        this.state.pendingEntries = data.pending_entries || 0;
        this.state.approvedEntries = data.approved_entries || 0;
        this.state.entries = data.recent_entries || [];
        this.state.projects = data.projects || [];
        this.state.workers = data.workers || [];
    }
    
    formatDuration(hours) {
        const h = Math.floor(hours);
        const m = Math.round((hours - h) * 60);
        return `${h}h ${m}m`;
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }
}

ConstructionTimeDashboard.template = "vdm_construction_time_tracker.ConstructionTimeDashboard";

registry.category("actions").add("construction_time_tracker_dashboard", ConstructionTimeDashboard);
