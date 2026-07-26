# -*- coding: utf-8 -*-
{
    'name': 'Construction Time Tracker',
    'summary': 'Track labor hours, phases, workers, and costs for construction projects',
    'version': '19.0.1.0.0',
    'category': 'Services/Project',
    'description': """
        Construction Time Tracker
        =========================

        Track time on construction projects with:
        - Timer per phase/work order
        - Worker time sheets
        - Cost calculations
        - Real-time OWL dashboard
        - PDF reports
    """,
    'author': 'Farid SLIMANI',
    'website': 'https://imazighenapps.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 79,
    'currency': 'EUR',
    'depends': [
        'project',
        'hr',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/stages.xml',
        'data/cron.xml',
        'views/time_entry_views.xml',
        'views/project_views.xml',
        'views/worker_views.xml',
        'views/cost_report_views.xml',
        'views/dashboard.xml',
        'report/time_entry_report.xml',
        'report/time_report_template.xml',
        'report/daily_summary_wizard.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vdm_construction_time_tracker/static/src/css/dashboard.css',
            'vdm_construction_time_tracker/static/src/js/dashboard.js',
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
