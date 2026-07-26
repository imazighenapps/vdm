import json
import urllib.request
import urllib.error
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AiChatbotConfig(models.Model):
    _name = 'ai.chatbot.config'
    _description = 'AI Chatbot Configuration'

    name = fields.Char(string='Configuration Name', required=True, default='Default Chatbot')
    provider = fields.Selection([
        ('openai', 'OpenAI (GPT)'),
        ('anthropic', 'Anthropic (Claude)'),
        ('deepseek', 'DeepSeek'),
        ('ollama', 'Ollama (Local)'),
    ], string='AI Provider', required=True, default='openai')
    api_key = fields.Text(string='API Key')
    model = fields.Char(string='Model', default='gpt-4o-mini')
    ollama_url = fields.Char(string='Ollama URL', default='http://localhost:11434')
    system_prompt = fields.Text(string='System Prompt', default="""You are a helpful sales assistant for {company_name}.
Your role is to:
1. Greet customers professionally
2. Answer questions about products and services
3. Qualify leads by asking about their needs
4. Schedule appointments when requested
5. Escalate to a human agent when needed

Be concise, friendly, and professional.
Always respond in the customer's language.
Never make up information - if you don't know, say so.""")
    welcome_message = fields.Text(string='Welcome Message',
        default="Hello! I'm your AI assistant. How can I help you today?")
    fallback_message = fields.Text(string='Fallback Message',
        default="I'm not sure I understand. Let me connect you with a human agent.")
    max_tokens = fields.Integer(string='Max Tokens', default=500)
    temperature = fields.Float(string='Temperature', default=0.7, digits=(3, 2))
    active = fields.Boolean(string='Active', default=True)
    whatsapp_enabled = fields.Boolean(string='WhatsApp Enabled', default=False)
    whatsapp_phone = fields.Char(string='WhatsApp Phone Number')
    whatsapp_token = fields.Text(string='WhatsApp Access Token')
    website_enabled = fields.Boolean(string='Website Chat Enabled', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    conversation_ids = fields.One2many('ai.chatbot.conversation', 'config_id', string='Conversations')
    total_conversations = fields.Integer(string='Total Conversations', compute='_compute_stats')
    total_messages = fields.Integer(string='Total Messages', compute='_compute_stats')

    @api.depends('conversation_ids', 'conversation_ids.message_ids')
    def _compute_stats(self):
        for rec in self:
            rec.total_conversations = len(rec.conversation_ids)
            rec.total_messages = sum(len(c.message_ids) for c in rec.conversation_ids)

    def get_ai_response(self, conversation_id, user_message):
        self.ensure_one()
        conversation = self.env['ai.chatbot.conversation'].browse(conversation_id)

        messages = [{'role': 'system', 'content': self.system_prompt.replace('{company_name}', self.company_id.name)}]

        for msg in conversation.message_ids[-10:]:
            role = 'assistant' if msg.sender_type == 'bot' else 'user'
            messages.append({'role': role, 'content': msg.body})

        messages.append({'role': 'user', 'content': user_message})

        try:
            if self.provider == 'ollama':
                url = f"{self.ollama_url}/api/chat"
                payload = json.dumps({
                    'model': self.model,
                    'messages': messages,
                    'stream': False,
                }).encode('utf-8')
                headers = {'Content-Type': 'application/json'}
            elif self.provider == 'openai':
                url = 'https://api.openai.com/v1/chat/completions'
                payload = json.dumps({
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': self.max_tokens,
                    'temperature': self.temperature,
                }).encode('utf-8')
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                }
            elif self.provider == 'anthropic':
                url = 'https://api.anthropic.com/v1/messages'
                system_msg = messages[0]['content'] if messages[0]['role'] == 'system' else ''
                user_messages = [m for m in messages if m['role'] != 'system']
                payload = json.dumps({
                    'model': self.model,
                    'max_tokens': self.max_tokens,
                    'system': system_msg,
                    'messages': user_messages,
                }).encode('utf-8')
                headers = {
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json',
                }
            elif self.provider == 'deepseek':
                url = 'https://api.deepseek.com/v1/chat/completions'
                payload = json.dumps({
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': self.max_tokens,
                    'temperature': self.temperature,
                }).encode('utf-8')
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                }
            else:
                return self.fallback_message

            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            if self.provider == 'ollama':
                return result.get('message', {}).get('content', self.fallback_message)
            elif self.provider == 'anthropic':
                content = result.get('content', [])
                if content:
                    return content[0].get('text', self.fallback_message)
                return self.fallback_message
            else:
                choices = result.get('choices', [])
                if choices:
                    return choices[0].get('message', {}).get('content', self.fallback_message)
                return self.fallback_message

        except Exception as e:
            _logger.error('AI response error: %s', str(e))
            return self.fallback_message

    def _detect_appointment_intent(self, message):
        appointment_keywords = [
            'rendez-vous', 'rdv', 'appointment', 'schedule', 'book',
            'planner', 'réserver', 'disponible', 'available', 'horaire',
            'calendrier', 'calendar', 'meeting', 'réunion',
        ]
        return any(keyword in message.lower() for keyword in appointment_keywords)

    def _detect_escalation_intent(self, message):
        escalation_keywords = [
            'humain', 'human', 'agent', 'personne', 'someone',
            'parler', 'speak', 'manager', 'responsable',
            'plaindre', 'complaint', 'problème', 'problem',
        ]
        return any(keyword in message.lower() for keyword in escalation_keywords)
