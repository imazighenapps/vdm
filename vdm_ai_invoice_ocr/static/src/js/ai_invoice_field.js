/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class AiDigitizeButton extends Component {
    setup() {
        this.state = useState({
            loading: false,
            lastResult: null,
        });
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
    }

    async onClick() {
        const record = this.props.record;
        if (!record || record.isNew) {
            this.notification.add(_t("Please save the invoice first."), {
                type: "warning",
            });
            return;
        }

        this.state.loading = true;

        try {
            const wizardAction = await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "ai.invoice.digitize.wizard",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context: {
                    default_invoice_id: record.resId,
                },
            });

            this.state.lastResult = wizardAction;
        } catch (error) {
            this.notification.add(_t("Error opening AI digitize wizard: ") + error.message, {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }
}

AiDigitizeButton.template = "vdm_ai_invoice_ocr.AiDigitizeButton";

registry.category("fields").add("ai_digitize_button", AiDigitizeButton);
