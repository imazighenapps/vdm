# -*- coding: utf-8 -*-
{
    'name': 'Audit Trail Pro',
    'summary': 'Professional audit trail solution for security, compliance and traceability in Odoo 19',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'description': """
        Audit Trail Pro
        ===============

        Professional audit trail solution for Odoo 19.
        Track all important actions for security, compliance and traceability.

        Features:
        - Create/Update/Delete tracking with full details
        - Field-level change history
        - Connection logging (login/logout/failed)
        - Export, print, email audit
        - Rights and settings audit
        - Real-time OWL dashboard
        - Alert system with configurable rules
        - Risk scoring per user
        - Advanced search and filtering
        - Automatic log cleanup
        - Performance optimized
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps.com@gmail.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 49,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'data/default_alerts.xml',
        'views/audit_log_views.xml',
        'views/audit_alert_views.xml',
        'views/audit_config_views.xml',
        'views/audit_dashboard.xml',
        'views/res_config_settings_views.xml',
        'views/menu.xml',
        'wizard/audit_log_wizard.xml',
        'report/audit_log_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'audit_trail_pro/static/src/css/dashboard.css',
            'audit_trail_pro/static/src/js/dashboard.js',
        ],
    },
     'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 100,
}
