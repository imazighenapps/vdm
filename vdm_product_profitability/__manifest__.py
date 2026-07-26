# -*- coding: utf-8 -*-
{
    'name': 'Product Profitability Report',
    'summary': 'Analyze product profitability with margin analysis, cost tracking, and detailed reports',
    'version': '19.0.1.0.0',
    'category': 'Services/Sales',
    'description': """
        Product Profitability Report
        ===========================

        Analyze product profitability with:
        - Margin analysis per product
        - Cost vs selling price tracking
        - Customer profitability analysis
        - Category-based reporting
        - Real-time OWL dashboard
        - PDF and Excel export
    """,
    'author': 'Farid SLIMANI',
    'website': 'https://imazighenapps.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 59,
    'currency': 'EUR',
    'depends': [
        'sale',
        'account',
        'stock',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/profitability_views.xml',
        'views/dashboard.xml',
        'report/profitability_report.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vdm_product_profitability/static/src/css/dashboard.css',
            'vdm_product_profitability/static/src/js/dashboard.js',
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
