# -*- coding: utf-8 -*-
{
    'name': 'AI Sales Chatbot for WhatsApp & Website',
    'version': '19.0.1.0.0',
    'category': 'Marketing/CRM',
    'summary': 'Qualify leads and answer questions with AI on WhatsApp & website',
    'description': """
AI Sales Chatbot for WhatsApp & Website
=========================================

Qualify leads and answer questions with AI on WhatsApp & your website.
24/7 automated support — never miss a sales opportunity.

Features:
- WhatsApp Business API integration
- Embeddable website chat widget
- Multi-AI: GPT, Claude, DeepSeek, Ollama (local)
- Automatic CRM lead creation with conversation history
- Smart escalation with intent detection
- Configurable qualification questions per industry
- Analytics dashboard with real-time metrics
- Multi-language support
- Multi-company support

Built for Odoo 19 (OWL 3, <list> views, model_create_multi).
    """,

    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 59.00,
    'currency': 'EUR',

    'depends': [
        'crm',
        'website',
        'mail',
    ],

    'external_dependencies': {},

    'data': [
        # Security
        'security/ai_chatbot_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/ir_config_parameter_data.xml',

        # Views
        'views/ai_chatbot_config_views.xml',
        'views/ai_chatbot_conversation_views.xml',
        'views/ai_chatbot_dashboard.xml',
        'views/res_config_settings_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'vdm_ai_sales_chatbot/static/src/js/ai_chatbot_component.js',
            'vdm_ai_sales_chatbot/static/src/xml/ai_chatbot_component.xml',
        ],
        'web.assets_frontend': [
            'vdm_ai_sales_chatbot/static/src/js/ai_chatbot_component.js',
            'vdm_ai_sales_chatbot/static/src/xml/ai_chatbot_component.xml',
        ],
    },

    'images': [
        'static/description/banner_chatbot.png',
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
