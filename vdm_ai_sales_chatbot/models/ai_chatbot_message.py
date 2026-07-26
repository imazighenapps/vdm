from odoo import models, fields, api


class AiChatbotMessage(models.Model):
    _name = 'ai.chatbot.message'
    _description = 'AI Chatbot Message'
    _order = 'timestamp asc'

    conversation_id = fields.Many2one('ai.chatbot.conversation', string='Conversation', required=True, ondelete='cascade')
    body = fields.Text(string='Message', required=True)
    sender_type = fields.Selection([
        ('customer', 'Customer'),
        ('bot', 'Bot'),
        ('agent', 'Agent'),
    ], string='Sender Type', required=True)
    sender_name = fields.Char(string='Sender Name')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    channel = fields.Selection(related='conversation_id.channel', string='Channel')
    is_read = fields.Boolean(string='Read', default=False)
