from odoo.tests.common import TransactionCase


class TestAiChatbot(TransactionCase):

    def setUp(self):
        super().setUp()
        self.config = self.env['ai.chatbot.config'].create({
            'name': 'Test Bot',
            'provider': 'openai',
            'api_key': 'test-key',
            'model': 'gpt-4o-mini',
            'system_prompt': 'You are a test bot for {company_name}.',
            'welcome_message': 'Hello! How can I help?',
        })

    def test_config_creation(self):
        self.assertEqual(self.config.provider, 'openai')
        self.assertTrue(self.config.active)

    def test_conversation_creation(self):
        conv = self.env['ai.chatbot.conversation'].create({
            'config_id': self.config.id,
            'channel': 'website',
            'contact_name': 'Test User',
        })
        self.assertEqual(conv.status, 'active')
        self.assertEqual(conv.channel, 'website')

    def test_message_creation(self):
        conv = self.env['ai.chatbot.conversation'].create({
            'config_id': self.config.id,
            'channel': 'whatsapp',
            'contact_phone': '+1234567890',
        })
        msg = self.env['ai.chatbot.message'].create({
            'conversation_id': conv.id,
            'body': 'Hello!',
            'sender_type': 'customer',
        })
        self.assertEqual(msg.sender_type, 'customer')
        self.assertEqual(conv.message_count, 1)

    def test_escalation_detection(self):
        self.assertTrue(self.config._detect_escalation_intent('I want to speak to a human'))
        self.assertFalse(self.config._detect_escalation_intent('Hello'))

    def test_appointment_detection(self):
        self.assertTrue(self.config._detect_appointment_intent('I want to schedule an appointment'))
        self.assertFalse(self.config._detect_appointment_intent('What products do you have?'))

    def test_conversation_close(self):
        conv = self.env['ai.chatbot.conversation'].create({
            'config_id': self.config.id,
            'channel': 'website',
        })
        conv.action_close()
        self.assertEqual(conv.status, 'closed')
