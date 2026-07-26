import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AiChatbotWebhook(http.Controller):

    @http.route('/ai-chatbot/whatsapp/webhook', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def whatsapp_webhook(self, **kwargs):
        data = request.jsonrequest
        _logger.info('WhatsApp webhook received: %s', json.dumps(data)[:500])

        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        messages = value.get('messages', [])
                        contacts = value.get('contacts', [])

                        for msg in messages:
                            self._process_whatsapp_message(msg, contacts)

        return {'status': 'ok'}

    def _process_whatsapp_message(self, msg, contacts):
        phone = msg.get('from', '')
        text = ''
        for part in msg.get('messages', [msg]):
            if part.get('type') == 'text':
                text = part.get('text', {}).get('body', '')
            elif part.get('type') == 'image':
                text = '[Image received]'
            elif part.get('type') == 'document':
                text = '[Document received]'

        if not text:
            return

        config = request.env['ai.chatbot.config'].sudo().search([
            ('whatsapp_enabled', '=', True),
            ('active', '=', True),
        ], limit=1)

        if not config:
            _logger.warning('No active WhatsApp chatbot config found')
            return

        partner = request.env['res.partner'].sudo().search([
            ('phone', 'ilike', phone),
        ], limit=1)

        conversation = request.env['ai.chatbot.conversation'].sudo().search([
            ('config_id', '=', config.id),
            ('contact_phone', '=', phone),
            ('status', '=', 'active'),
        ], limit=1)

        if not conversation:
            contact_name = ''
            if contacts:
                contact_name = contacts[0].get('profile', {}).get('name', '')

            conversation = request.env['ai.chatbot.conversation'].sudo().create({
                'config_id': config.id,
                'channel': 'whatsapp',
                'contact_name': contact_name,
                'contact_phone': phone,
                'partner_id': partner.id if partner else False,
            })

        request.env['ai.chatbot.message'].sudo().create({
            'conversation_id': conversation.id,
            'body': text,
            'sender_type': 'customer',
            'sender_name': conversation.contact_name,
        })

        if config._detect_escalation_intent(text):
            conversation.sudo().action_escalate()
            request.env['ai.chatbot.message'].sudo().create({
                'conversation_id': conversation.id,
                'body': config.fallback_message,
                'sender_type': 'bot',
            })
            return

        ai_response = config.sudo().get_ai_response(conversation.id, text)

        request.env['ai.chatbot.message'].sudo().create({
            'conversation_id': conversation.id,
            'body': ai_response,
            'sender_type': 'bot',
        })

        self._send_whatsapp_message(config, phone, ai_response)

    def _send_whatsapp_message(self, config, phone, text):
        import urllib.request

        if not config.whatsapp_token or not config.whatsapp_phone:
            return

        try:
            url = f"https://graph.facebook.com/v18.0/{config.whatsapp_phone}/messages"
            payload = json.dumps({
                'messaging_product': 'whatsapp',
                'to': phone,
                'type': 'text',
                'text': {'body': text},
            }).encode('utf-8')

            req = urllib.request.Request(url, data=payload, headers={
                'Authorization': f'Bearer {config.whatsapp_token}',
                'Content-Type': 'application/json',
            })
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            _logger.error('Failed to send WhatsApp message: %s', str(e))

    @http.route('/ai-chatbot/website/chat', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def website_chat(self, **kwargs):
        data = request.jsonrequest
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', False)
        session_id = data.get('session_id', '')

        if not message:
            return {'error': 'No message provided'}

        config = request.env['ai.chatbot.config'].sudo().search([
            ('website_enabled', '=', True),
            ('active', '=', True),
        ], limit=1)

        if not config:
            return {'error': 'No active chatbot config'}

        if conversation_id:
            conversation = request.env['ai.chatbot.conversation'].sudo().browse(conversation_id)
        else:
            conversation = request.env['ai.chatbot.conversation'].sudo().create({
                'config_id': config.id,
                'channel': 'website',
                'contact_name': data.get('name', 'Website Visitor'),
                'contact_email': data.get('email', ''),
            })

        request.env['ai.chatbot.message'].sudo().create({
            'conversation_id': conversation.id,
            'body': message,
            'sender_type': 'customer',
        })

        if config._detect_escalation_intent(message):
            conversation.sudo().action_escalate()
            response = config.fallback_message
        else:
            response = config.sudo().get_ai_response(conversation.id, message)

        request.env['ai.chatbot.message'].sudo().create({
            'conversation_id': conversation.id,
            'body': response,
            'sender_type': 'bot',
        })

        return {
            'response': response,
            'conversation_id': conversation.id,
        }

    @http.route('/ai-chatbot/website/history', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def website_history(self, **kwargs):
        data = request.jsonrequest
        conversation_id = data.get('conversation_id', False)

        if not conversation_id:
            return {'messages': []}

        conversation = request.env['ai.chatbot.conversation'].sudo().browse(conversation_id)
        messages = []
        for msg in conversation.message_ids:
            messages.append({
                'body': msg.body,
                'sender_type': msg.sender_type,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else False,
            })

        return {'messages': messages}
