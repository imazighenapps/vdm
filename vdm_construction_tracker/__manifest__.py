# -*- coding: utf-8 -*-
{
    'name': 'Construction Project Tracker',
    'version': '19.0.1.0.0',
    'category': 'Project/Construction',
    'summary': 'Complete construction project management: BOQ, DPR, billing, subcontracts',
    'description': """
Construction Project Tracker
==============================

Complete construction project management for Odoo 19.

Manage construction projects with Bill of Quantities, Daily Progress Reports,
RA Billing, Change Orders, Subcontractors, and an interactive OWL 3 Dashboard.

Features:
- Project & Phase management with Gantt view
- Bill of Quantities (BOQ) with revision tracking
- Daily Progress Reports (DPR) with photo geolocation
- RA Billing with retention and advance recovery
- Change Order management with approval workflow
- Subcontractor management with measurement book
- OWL 3 interactive dashboard
- PDF reports for BOQ, DPR, and billing
- Multi-company support

Built for Odoo 19 (OWL 3, <list> views, model_create_multi).
    """,

    'author': 'Farid SLIMANI',
    'website': 'mailto:imazighenapps@gmail.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 99.00,
    'currency': 'EUR',

    'depends': [
        'project',
        'purchase',
        'stock',
        'account',
        'hr',
        'mail',
    ],

    'external_dependencies': {},

    'data': [
        'construction_core/security/construction_security.xml',
        'construction_core/security/ir.model.access.csv',
        'construction_core/data/sequence_data.xml',
        'construction_core/views/construction_project_views.xml',
        'construction_core/views/construction_phase_views.xml',
        'construction_core/views/construction_work_order_views.xml',
        'construction_core/views/construction_expense_views.xml',
        'construction_core/views/construction_dashboard_action.xml',
        'construction_core/views/construction_menu.xml',

        'construction_boq/security/ir.model.access.csv',
        'construction_boq/data/sequence_data.xml',
        'construction_boq/views/construction_boq_views.xml',
        'construction_boq/views/construction_boq_line_views.xml',

        'construction_site/security/ir.model.access.csv',
        'construction_site/data/sequence_data.xml',
        'construction_site/views/construction_site_diary_views.xml',
        'construction_site/views/construction_photo_views.xml',

        'construction_billing/security/ir.model.access.csv',
        'construction_billing/data/sequence_data.xml',
        'construction_billing/views/construction_change_order_views.xml',
        'construction_billing/views/construction_ra_billing_views.xml',

        'construction_subcontract/security/ir.model.access.csv',
        'construction_subcontract/data/sequence_data.xml',
        'construction_subcontract/views/construction_subcontract_views.xml',

        'construction_reports/data/ir_actions_report_data.xml',
        'construction_reports/report/construction_boq_report.xml',
        'construction_reports/report/construction_dpr_report.xml',
        'construction_reports/report/construction_billing_report.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'vdm_construction_tracker/static/src/js/construction_dashboard.js',
            'vdm_construction_tracker/static/src/xml/construction_dashboard.xml',
            'vdm_construction_tracker/static/src/css/construction_dashboard.css',
        ],
    },

    'images': [
        'static/description/banner_construction.png',
        
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
