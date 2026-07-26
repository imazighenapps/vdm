/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FleetManagementDashboard extends Component {
    setup() {
        this.state = useState({
            totalVehicles: 0,
            activeVehicles: 0,
            maintenanceVehicles: 0,
            inactiveVehicles: 0,
            totalCost: 0,
            recentMaintenance: [],
            recentFuel: [],
            upcomingInsurance: [],
        });
        
        this.rpc = useService("rpc");
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }
    
    async loadDashboardData() {
        const data = await this.rpc("/fleet/management/dashboard/data", {});
        this.state.totalVehicles = data.total_vehicles || 0;
        this.state.activeVehicles = data.active_vehicles || 0;
        this.state.maintenanceVehicles = data.maintenance_vehicles || 0;
        this.state.inactiveVehicles = data.inactive_vehicles || 0;
        this.state.totalCost = data.total_cost || 0;
        this.state.recentMaintenance = data.recent_maintenance || [];
        this.state.recentFuel = data.recent_fuel || [];
        this.state.upcomingInsurance = data.upcoming_insurance || [];
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }
}

FleetManagementDashboard.template = "vdm_fleet_management_plus.FleetManagementDashboard";

registry.category("actions").add("fleet_management_plus_dashboard", FleetManagementDashboard);
