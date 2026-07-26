{
    'name': 'ESG Carbon Tracker',
    'version': '18.0.1.0.0',
    'summary': 'Advanced GHG Protocol carbon accounting with Scope 1-3 tracking, CSRD/ESRS E1 compliance, and reduction targets',
    'description': """
        ESG Carbon Tracker for Odoo 19
        =================================

        Comprehensive carbon emissions management aligned with the GHG Protocol and EU CSRD/ESRS E1 standards.

        Features:
        - Scope 1, 2, and 3 emissions tracking across 15 GHG Protocol categories
        - Location-based and market-based Scope 2 calculations
        - Multi-gas breakdown (CO2, CH4, N2O, HFCs, PFCs, SF6)
        - Carbon intensity ratios (tCO2e per €M revenue, per employee)
        - Reduction targets with SBTi alignment tracking
        - Carbon offset and credit management
        - Year-over-year trend analysis with base year management
        - Anomaly detection for unusual emissions patterns
        - Board-ready PDF reports and executive dashboards
        - CSRD/ESRS E1 compliant reporting structure
        - DEFRA, EPA, ecoinvent emission factor database import
        - AI-assisted emission factor matching

        Perfect for companies subject to EU CSRD reporting requirements
        or those pursuing Science-Based Targets initiative (SBTi) validation.
    """,
    'author': 'Farid SLIMANI',
    'website': 'mailto:imazighenapps@gmail.com',
    'support': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 79.00,
    'currency': 'EUR',
    'application': True,
    'auto_install': False,
    'depends': [
        'mail',
        'account',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/esg_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/emission_factor_data.xml',
        'data/cron_data.xml',
        'views/esg_config_views.xml',
        'views/esg_emission_factor_views.xml',
        'views/esg_emission_line_views.xml',
        'views/esg_carbon_inventory_views.xml',
        'views/esg_carbon_offset_views.xml',
        'views/esg_reduction_target_views.xml',
        'views/esg_menu.xml',
        'wizards/emission_import_wizard_views.xml',
        'report/report_actions.xml',
        'report/carbon_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vdm_esg_carbon_tracker/static/src/js/esg_dashboard.js',
            'vdm_esg_carbon_tracker/static/src/xml/esg_dashboard.xml',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'sequence': 45,
}
