{
    'name': 'Invoice Chaser Pro',
    'version': '19.0.1.0.0',
    'summary': 'Automated payment reminders for overdue invoices with escalation levels and dashboard',
    'description': """
        Invoice Chaser Pro for Odoo 19
        ================================

        Automate your payment collection with intelligent invoice reminders.

        Features:
        - Automated reminders at J+7, J+15, J+30, J+60 after due date
        - 3 escalation levels: Gentle, Firm, Legal Notice
        - Dashboard showing overdue invoices by age and amount
        - Email templates for each reminder level
        - One-click bulk reminder for all overdue invoices
        - Manager escalation for high-value overdue invoices
        - Complete reminder history with audit trail
        - Multi-company ready

        Reduce your DSO (Days Sales Outstanding) by 30-50%.
    """,
    'author': 'Farid SLIMANI',
    'website': 'mailto:imazighenapps@gmail.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 49.00,
    'currency': 'EUR',
    'application': True,
    'auto_install': False,
    'depends': [
        'account',
        'mail',
    ],
    'external_dependencies': {},
    'data': [
        'security/invoice_chaser_security.xml',
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'data/cron_data.xml',
        'views/invoice_chaser_config_views.xml',
        'views/account_move_views.xml',
        'views/invoice_reminder_log_views.xml',
        'views/invoice_chaser_dashboard_views.xml',
        'views/invoice_chaser_menu.xml',
        'controllers/main.py',
        'report/invoice_chaser_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vdm_invoice_chaser/static/src/js/chaser_dashboard.js',
            'vdm_invoice_chaser/static/src/xml/chaser_dashboard.xml',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'sequence': 45,
}
