# -*- coding: utf-8 -*-
{
    'name': 'AI Invoice Digitization Pro',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Invoicing',
    'summary': 'AI-powered invoice extraction with 5 providers, self-learning, and cross-validation',
    'description': """
AI Invoice Digitization Pro
============================

Replace manual data entry with AI-powered invoice extraction.
5 providers, self-learning, and cross-validation — 98%+ accuracy in seconds.

Features:
- 5 AI providers: Claude, GPT-4o, Gemini, DeepSeek, Mistral
- Local Ollama support for fully private extraction
- 3 extraction modes: Guided, Simplified, Free (raw JSON)
- Self-learning vendor memory with correction history
- Cross-validation: math verification, tax matching, vendor matching
- QR code extraction for e-invoices
- PDF, JPG, PNG input support
- Line-item extraction with tax mapping
- Multi-company support

Built for Odoo 19 (OWL 3, <list> views, model_create_multi).
    """,

    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 39.00,
    'currency': 'EUR',

    'depends': [
        'account',
        'mail',
    ],

    'external_dependencies': {},

    'data': [
        # Security
        'security/ai_invoice_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/ir_config_parameter_data.xml',

        # Views
        'views/ai_invoice_menu.xml',
        'views/ai_invoice_config_views.xml',
        'views/ai_invoice_digitize_views.xml',
        'views/ai_invoice_digitize_wizard_views.xml',
        'views/ai_vendor_memory_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'vdm_ai_invoice_ocr/static/src/js/ai_invoice_field.js',
            'vdm_ai_invoice_ocr/static/src/xml/ai_invoice_field.xml',
        ],
    },

    'images': [
        'static/description/banner_ocr.png',
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
