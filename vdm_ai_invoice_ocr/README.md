# AI Invoice Digitization Pro

AI-powered invoice digitization module for Odoo 19 with multi-provider support.

## Features

- **Multi-Provider AI**: Claude, GPT-4o, Gemini, DeepSeek, Mistral
- **Guided Extraction**: Full context with accounts and taxes from your Odoo
- **Self-Learning**: Learns from your corrections per vendor
- **Cross-Validation**: Mathematical verification of totals, taxes, and line items
- **Smart Matching**: Automatic vendor and tax matching

## Requirements

- Odoo 19.0
- Python 3.10+
- API key from supported AI provider

## Installation

1. Copy `vdm_ai_invoice_ocr` to your Odoo addons path
2. Update the app list in Odoo
3. Install "AI Invoice Digitization Pro"

## Configuration

1. Go to **Accounting > Configuration > AI Invoice Config**
2. Create a new configuration
3. Select your AI provider
4. Enter your API key
5. Configure extraction mode and options

## Usage

1. Open a vendor bill in draft state
2. Click **AI Digitize** button
3. Review extracted data
4. Click **Apply to Invoice**

## Supported Providers

| Provider | Model | API URL |
|----------|-------|---------|
| Anthropic | claude-haiku-4-20250514 | api.anthropic.com |
| OpenAI | gpt-4o | api.openai.com |
| Google | gemini-pro | generativelanguage.googleapis.com |
| DeepSeek | deepseek-chat | api.deepseek.com |
| Mistral | mistral-large | api.mistral.ai |

## License

LGPL-3
