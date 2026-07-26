# -*- coding: utf-8 -*-
{
    'name': 'Fleet Management Plus',
    'summary': 'Complete fleet management with vehicle tracking, maintenance, fuel, and cost analysis',
    'version': '19.0.1.0.0',
    'category': 'Services/Fleet',
    'description': """
        Fleet Management Plus
        =====================

        Complete fleet management solution with:
        - Vehicle tracking and management
        - Preventive maintenance scheduling
        - Fuel consumption tracking
        - Insurance and contract management
        - Cost analysis and reporting
        - Real-time OWL dashboard
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 79,
    'currency': 'EUR',
    'depends': [
        'fleet',
        'hr',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/stages.xml',
        'data/cron.xml',
        'views/vehicle_views.xml',
        'views/maintenance_views.xml',
        'views/fuel_views.xml',
        'views/insurance_views.xml',
        'views/cost_views.xml',
        'views/dashboard.xml',
        'report/vehicle_report.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vdm_fleet_management_plus/static/src/css/dashboard.css',
            'vdm_fleet_management_plus/static/src/js/dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
