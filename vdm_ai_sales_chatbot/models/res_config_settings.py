from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_chatbot_enabled = fields.Boolean(
        string='Enable AI Chatbot',
        config_parameter='ai_chatbot.enabled',
    )
    ai_chatbot_default_provider = fields.Selection([
        ('openai', 'OpenAI (GPT)'),
        ('anthropic', 'Anthropic (Claude)'),
        ('deepseek', 'DeepSeek'),
        ('ollama', 'Ollama (Local)'),
    ], string='Default AI Provider',
        config_parameter='ai_chatbot.default_provider',
        default='openai',
    )
