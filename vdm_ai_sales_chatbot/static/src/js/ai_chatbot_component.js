/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class AiChatbotComponent extends Component {
    setup() {
        this.state = useState({
            messages: [],
            inputMessage: "",
            conversationId: false,
            isOpen: false,
            isLoading: false,
        });
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen && !this.state.conversationId) {
            this.addBotMessage("Hello! I'm your AI assistant. How can I help you today?");
        }
    }

    addBotMessage(body) {
        this.state.messages.push({
            body,
            sender_type: "bot",
            timestamp: new Date().toISOString(),
        });
    }

    async sendMessage() {
        const message = this.state.inputMessage.trim();
        if (!message) return;

        this.state.messages.push({
            body: message,
            sender_type: "customer",
            timestamp: new Date().toISOString(),
        });
        this.state.inputMessage = "";
        this.state.isLoading = true;

        try {
            const data = await rpc("/ai-chatbot/website/chat", {
                message,
                conversation_id: this.state.conversationId,
            });

            if (data.conversation_id) {
                this.state.conversationId = data.conversation_id;
            }
            if (data.response) {
                this.addBotMessage(data.response);
            }
        } catch (error) {
            this.addBotMessage("Sorry, something went wrong. Please try again.");
        } finally {
            this.state.isLoading = false;
        }
    }

    onKeydown(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
}

AiChatbotComponent.template = "vdm_ai_sales_chatbot.AiChatbotComponent";
