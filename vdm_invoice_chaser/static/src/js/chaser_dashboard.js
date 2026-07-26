/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class ChaserDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        
        this.state = useState({
            loading: true,
            summary: {},
            topOverdue: [],
            recentLogs: [],
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            const data = await this.rpc("/invoice_chaser/dashboard/data", {});
            this.state.summary = data.summary || {};
            this.state.topOverdue = data.top_overdue || [];
            this.state.recentLogs = data.recent_logs || [];
        } catch (error) {
            console.error("Failed to load dashboard:", error);
        } finally {
            this.state.loading = false;
        }
    }

    navigateToOverdue() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Overdue Invoices',
            res_model: 'account.move',
            view_mode: 'list,form',
            domain: [
                ['move_type', 'in', ['out_invoice', 'out_refund']],
                ['state', '=', 'posted'],
                ['payment_state', '!=', 'paid'],
            ],
        });
    }

    sendAllReminders() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Send Reminders',
            res_model: 'account.move',
            view_mode: 'list',
            domain: [
                ['move_type', 'in', ['out_invoice', 'out_refund']],
                ['state', '=', 'posted'],
                ['payment_state', '!=', 'paid'],
            ],
        });
    }

    navigateToLogs() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Reminder History',
            res_model: 'invoice.reminder.log',
            view_mode: 'list,form',
        });
    }
}

ChaserDashboard.template = "vdm_invoice_chaser.ChaserDashboard";

registry.category("actions").add("chaser_dashboard", ChaserDashboard);

export default ChaserDashboard;
