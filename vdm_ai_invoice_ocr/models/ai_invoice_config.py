from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AiInvoiceConfig(models.Model):
    _name = 'ai.invoice.config'
    _description = 'AI Invoice Digitization Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    provider = fields.Selection([
        ('anthropic', 'Anthropic (Claude)'),
        ('openai', 'OpenAI (GPT-4o)'),
        ('google', 'Google (Gemini)'),
        ('deepseek', 'DeepSeek'),
        ('mistral', 'Mistral AI'),
    ], string='AI Provider', required=True, default='anthropic')
    api_key = fields.Text(string='API Key', required=True)
    model = fields.Char(string='Model', default='claude-haiku-4-20250514')
    extraction_mode = fields.Selection([
        ('guided', 'Guided (Full Context)'),
        ('simplified', 'Simplified (Taxes Only)'),
        ('free', 'Free (Raw Extraction)'),
    ], string='Extraction Mode', default='guided')
    extract_lines = fields.Boolean(string='Extract Invoice Lines', default=True)
    auto_extract = fields.Boolean(string='Auto-Extract on Upload', default=False)
    background_extract = fields.Boolean(string='Background Extraction', default=False)
    qr_extraction = fields.Boolean(string='QR Code Extraction', default=True)
    learning_enabled = fields.Boolean(string='Self-Learning from Corrections', default=True)
    max_tokens = fields.Integer(string='Max Tokens', default=4096)
    temperature = fields.Float(string='Temperature', default=0.1, digits=(3, 2))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name, company_id)', 'Configuration name must be unique per company!')
    ]

    def get_provider_config(self):
        self.ensure_one()
        configs = {
            'anthropic': {
                'api_url': 'https://api.anthropic.com/v1/messages',
                'headers': {
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json',
                },
            },
            'openai': {
                'api_url': 'https://api.openai.com/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
            },
            'google': {
                'api_url': f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent',
                'headers': {
                    'Content-Type': 'application/json',
                },
                'params': {'key': self.api_key},
            },
            'deepseek': {
                'api_url': 'https://api.deepseek.com/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
            },
            'mistral': {
                'api_url': 'https://api.mistral.ai/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
            },
        }
        return configs.get(self.provider, {})
