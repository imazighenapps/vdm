# -*- coding: utf-8 -*-
{
    'name': 'CBAM Compliance Tracker',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Compliance',
    'summary': 'EU Carbon Border Adjustment Mechanism compliance for Odoo',
    'description': """
CBAM Compliance Tracker
========================

Track embedded emissions, manage certificates, and file quarterly CBAM reports
directly from your Odoo ERP system.

Features:
- Import event tracking with embedded emissions calculation
- CBAM certificate management with FIFO cost tracking
- Quarterly report generation with CSV/PDF export
- Dashboard with KPIs and deadline alerts
- Supplier registry with self-declaration workflow
- 6 sectors: Cement, Iron & Steel, Aluminium, Fertilizers, Electricity, Hydrogen
- Multi-company support
- Full audit trail for every import event

Built for Odoo 19 (OWL 3, <list> views, model_create_multi).
    """,

    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 49.00,
    'currency': 'EUR',

    'depends': [
        'account',
        'purchase',
        'stock',
    ],

    'data': [
        # Security
        'security/cbam_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence_data.xml',
        'data/cbam_sector_data.xml',
        'data/emission_factor_data.xml',

        # Views
        'views/cbam_product_views.xml',
        'views/cbam_supplier_views.xml',
        'views/cbam_import_event_views.xml',
        'views/cbam_certificate_views.xml',
        'views/cbam_quarterly_report_views.xml',
        'views/cbam_dashboard.xml',

        # Wizards
        'wizard/cbam_wizard_import_views.xml',

        # Reports
        'report/cbam_quarterly_report_template.xml',
        'report/cbam_annual_report_template.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'vdm_cbam_compliance/static/src/css/cbam_dashboard.css',
            'vdm_cbam_compliance/static/src/js/cbam_dashboard.js',
            'vdm_cbam_compliance/static/src/xml/cbam_dashboard.xml',
        ],
    },

    'images': [
        'static/description/banner_cbam.png',
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
