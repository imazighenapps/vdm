# AI Sales Chatbot WhatsApp

AI-powered sales chatbot module for Odoo 19 that integrates with WhatsApp and website chat.

## Features

- **Multi-Channel Support**: WhatsApp Business API and Website chat widget
- **AI Providers**: OpenAI (GPT), Anthropic (Claude), DeepSeek, Ollama (Local)
- **Lead Qualification**: Auto-qualify leads and create CRM opportunities
- **Smart Escalation**: Detects complex requests and transfers to human agents
- **Appointment Detection**: Identifies scheduling intent

## Requirements

- Odoo 19
- CRM module
- Website module

## Configuration

1. Install the module
2. Go to AI Chatbot > Configuration
3. Create a new chatbot configuration
4. Select your AI provider and enter API credentials
5. Enable WhatsApp or Website channels as needed

## WhatsApp Setup

1. Create a Meta Business account
2. Set up WhatsApp Business API
3. Configure webhook URL: `https://your-odoo-domain/ai-chatbot/whatsapp/webhook`
4. Enter your WhatsApp Phone Number and Access Token in the chatbot configuration

## License

LGPL-3
