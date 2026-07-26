from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestAiInvoiceDigitize(TransactionCase):

    def setUp(self):
        super().setUp()
        self.config = self.env['ai.invoice.config'].create({
            'name': 'Test Config',
            'provider': 'anthropic',
            'api_key': 'test-key-123',
            'model': 'claude-haiku-4-20250514',
            'extraction_mode': 'guided',
        })

    def test_config_creation(self):
        self.assertEqual(self.config.provider, 'anthropic')
        self.assertTrue(self.config.active)

    def test_validation_totals(self):
        digitize = self.env['ai.invoice.digitize']
        valid_data = {
            'subtotal': 100.0,
            'tax_amount': 20.0,
            'total_amount': 120.0,
            'invoice_date': '2026-01-01',
            'due_date': '2026-01-31',
            'lines': [{'amount': 100.0}],
        }
        errors = digitize._validate_extraction(valid_data)
        self.assertEqual(len(errors), 0)

    def test_validation_total_mismatch(self):
        digitize = self.env['ai.invoice.digitize']
        invalid_data = {
            'subtotal': 100.0,
            'tax_amount': 20.0,
            'total_amount': 150.0,
            'lines': [{'amount': 100.0}],
        }
        errors = digitize._validate_extraction(invalid_data)
        self.assertTrue(len(errors) > 0)
