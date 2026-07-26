/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Session } from "@web/session";

export class ConstructionDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            projects: [],
            stats: {
                total_projects: 0,
                active_projects: 0,
                total_value: 0,
                avg_progress: 0,
            },
            alerts: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            const data = await this.rpc("/construction/dashboard/data", {});
            this.state.projects = data.projects || [];
            this.state.stats = data.stats || this.state.stats;
            this.state.alerts = data.alerts || [];
        } catch (e) {
            console.error("Failed to load dashboard data:", e);
        } finally {
            this.state.loading = false;
        }
    }

    async openProject(projectId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Project",
            res_model: "construction.project",
            res_id: projectId,
            view_mode: "form",
            target: "current",
        });
    }

    async openAllProjects() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "All Projects",
            res_model: "construction.project",
            view_mode: "list,form",
            target: "current",
        });
    }

    async openDPR() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Daily Reports",
            res_model: "construction.site.diary",
            view_mode: "list,form",
            target: "current",
        });
    }

    async openBOQ() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Bill of Quantities",
            res_model: "construction.boq",
            view_mode: "list,form",
            target: "current",
        });
    }

    async openBilling() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "RA Billing",
            res_model: "construction.ra.billing",
            view_mode: "list,form",
            target: "current",
        });
    }

    async openChangeOrders() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Change Orders",
            res_model: "construction.change.order",
            view_mode: "list,form",
            target: "current",
        });
    }

    async openSubcontracts() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Subcontracts",
            res_model: "construction.subcontract",
            view_mode: "list,form",
            target: "current",
        });
    }

    getStateDecoration(state) {
        const decorations = {
            draft: "text-muted",
            confirmed: "text-info",
            in_progress: "text-primary",
            on_hold: "text-warning",
            completed: "text-success",
            cancelled: "text-danger",
        };
        return decorations[state] || "";
    }

    getStateLabel(state) {
        const labels = {
            draft: "Draft",
            confirmed: "Confirmed",
            in_progress: "In Progress",
            on_hold: "On Hold",
            completed: "Completed",
            cancelled: "Cancelled",
        };
        return labels[state] || state;
    }
}

ConstructionDashboard.template = "vdm_construction_tracker.ConstructionDashboard";

registry.category("actions").add("construction_dashboard", ConstructionDashboard);
