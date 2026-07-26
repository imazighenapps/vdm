# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestCbamWorkflow(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env['product.template'].create({
            'name': 'CBAM Steel Product',
            'cbam_covered': True,
            'cbam_sector': 'steel',
            'embedded_emission': 1.37,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'country_id': self.env.ref('base.us').id,
        })
        self.country = self.env.ref('base.us')

    def test_product_cbam_fields(self):
        self.assertTrue(self.product.cbam_covered)
        self.assertEqual(self.product.cbam_sector, 'steel')
        self.assertEqual(self.product.embedded_emission, 1.37)

    def test_import_event_creation(self):
        event = self.env['cbam.import.event'].create({
            'product_id': self.env['product.product'].create({
                'name': 'Steel Coil',
                'product_tmpl_id': self.product.id,
            }).id,
            'supplier_id': self.partner.id,
            'origin_country_id': self.country.id,
            'sector': 'steel',
            'quantity': 100.0,
            'import_date': '2026-01-15',
        })
        self.assertEqual(event.status, 'draft')
        self.assertAlmostEqual(event.total_emissions, 137.0, places=2)

    def test_import_event_workflow(self):
        event = self.env['cbam.import.event'].create({
            'product_id': self.env['product.product'].create({
                'name': 'Steel Bar',
                'product_tmpl_id': self.product.id,
            }).id,
            'supplier_id': self.partner.id,
            'origin_country_id': self.country.id,
            'sector': 'steel',
            'quantity': 50.0,
        })
        event.action_submit()
        self.assertEqual(event.status, 'submitted')
        event.action_confirm()
        self.assertEqual(event.status, 'confirmed')
        event.action_draft()
        self.assertEqual(event.status, 'draft')

    def test_certificate_creation(self):
        cert = self.env['cbam.certificate'].create({
            'purchase_date': '2026-01-01',
            'quantity': 1000,
            'price_per_unit': 65.0,
        })
        self.assertAlmostEqual(cert.total_cost, 65000.0, places=2)
        self.assertAlmostEqual(cert.remaining_quantity, 1000.0, places=2)
        self.assertEqual(cert.status, 'available')

    def test_quarterly_report_creation(self):
        report = self.env['cbam.quarterly.report'].create({
            'year': 2026,
            'quarter': 'Q1',
        })
        self.assertEqual(report.status, 'draft')
        self.assertIn('Q1', report.name)
        self.assertIn('2026', report.name)

    def test_quarterly_report_workflow(self):
        report = self.env['cbam.quarterly.report'].create({
            'year': 2026,
            'quarter': 'Q1',
        })
        report.action_submit()
        self.assertEqual(report.status, 'submitted')
        report.action_validate()
        self.assertEqual(report.status, 'validated')
        report.action_approve()
        self.assertEqual(report.status, 'approved')
        report.action_draft()
        self.assertEqual(report.status, 'draft')

    def test_supplier_effective_emission(self):
        supplier = self.env['cbam.supplier'].create({
            'name': 'Test Supplier Emission',
            'partner_id': self.partner.id,
            'product_tmpl_id': self.product.id,
            'actual_emission': 2.5,
            'default_emission': 1.37,
            'use_default_value': True,
        })
        self.assertAlmostEqual(supplier.effective_emission, 1.37, places=2)

        supplier.use_default_value = False
        self.assertAlmostEqual(supplier.effective_emission, 2.5, places=2)

    def test_product_validation(self):
        with self.assertRaises(ValidationError):
            self.env['product.template'].create({
                'name': 'Invalid CBAM Product',
                'cbam_covered': True,
                'embedded_emission': -1.0,
            })
