/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AuditTrailDashboard extends Component {
    setup() {
        this.state = useState({
            totalActions: 0,
            creates: 0,
            updates: 0,
            deletes: 0,
            logins: 0,
            exports: 0,
            prints: 0,
            emails: 0,
            activeUsers: 0,
            actionsByDay: {},
            actionsByUser: [],
            actionsByModel: [],
            highRiskUsers: [],
            recentAlerts: [],
            loading: true,
        });
        
        this.rpc = useService("rpc");
        this.action = useService("action");
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }
    
    async loadDashboardData() {
        try {
            const data = await this.rpc("/audit/trail/dashboard/data", {});
            
            if (data.error) {
                console.error("Dashboard error:", data.error);
                return;
            }
            
            this.state.totalActions = data.total_actions || 0;
            this.state.creates = data.creates || 0;
            this.state.updates = data.updates || 0;
            this.state.deletes = data.deletes || 0;
            this.state.logins = data.logins || 0;
            this.state.exports = data.exports || 0;
            this.state.prints = data.prints || 0;
            this.state.emails = data.emails || 0;
            this.state.activeUsers = data.active_users || 0;
            this.state.actionsByDay = data.actions_by_day || {};
            this.state.actionsByUser = data.actions_by_user || [];
            this.state.actionsByModel = data.actions_by_model || [];
            this.state.highRiskUsers = data.high_risk_users || [];
            this.state.recentAlerts = data.recent_alerts || [];
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load dashboard:", error);
            this.state.loading = false;
        }
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat('fr-FR').format(num);
    }
    
    viewLogs() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Audit Logs",
            res_model: "audit.trail.log",
            view_mode: "list,form,pivot,graph",
            target: "current",
        });
    }
    
    viewAlerts() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Alerts",
            res_model: "audit.trail.alert",
            view_mode: "list,form",
            target: "current",
        });
    }
    
    viewHighRiskUsers() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "High Risk Users",
            res_model: "res.users",
            view_mode: "list,form",
            domain: [["audit_risk_score", ">", 50]],
            target: "current",
        });
    }
    
    viewConfiguration() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Configuration",
            res_model: "audit.trail.config",
            view_mode: "form",
            target: "current",
        });
    }
    
    getDayName(dateStr) {
        const date = new Date(dateStr);
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return days[date.getDay()];
    }
    
    getMaxUserCount() {
        if (this.state.actionsByUser.length === 0) return 1;
        return Math.max(...this.state.actionsByUser.map(u => u.count));
    }
    
    getMaxModelCount() {
        if (this.state.actionsByModel.length === 0) return 1;
        return Math.max(...this.state.actionsByModel.map(m => m.count));
    }
}

AuditTrailDashboard.template = "audit_trail_pro.AuditTrailDashboard";

registry.category("actions").add("audit_trail_dashboard", AuditTrailDashboard);
