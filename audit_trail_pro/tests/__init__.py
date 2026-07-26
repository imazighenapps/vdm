# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessDenied


class TestAuditTrailLog(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Log = self.env['audit.trail.log']
        self.User = self.env['res.users']
        self.Company = self.env['res.company']
        
        # Create test company
        self.company = self.Company.create({
            'name': 'Test Company',
        })
        
        # Create test user
        self.test_user = self.User.create({
            'name': 'Test User',
            'login': 'test_audit_user',
            'password': 'test123',
            'company_id': self.company.id,
            'company_ids': [(6, 0, [self.company.id])],
        })

    def test_log_creation(self):
        """Test that audit logs are created."""
        initial_count = self.Log.search_count([])
        
        # Create a partner (this should trigger audit log)
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': self.company.id,
        })
        
        # Check that log was created
        new_count = self.Log.search_count([])
        self.assertGreater(new_count, initial_count)
        
        # Check log details
        log = self.Log.search([
            ('model_name', '=', 'res.partner'),
            ('record_id', '=', partner.id),
        ], limit=1)
        
        self.assertTrue(log)
        self.assertEqual(log.action_type, 'create')

    def test_log_update(self):
        """Test that field updates are logged."""
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': self.company.id,
        })
        
        initial_count = self.Log.search_count([
            ('model_name', '=', 'res.partner'),
            ('record_id', '=', partner.id),
            ('action_type', '=', 'update'),
        ])
        
        # Update partner
        partner.write({'name': 'Updated Partner'})
        
        # Check that update was logged
        new_count = self.Log.search_count([
            ('model_name', '=', 'res.partner'),
            ('record_id', '=', partner.id),
            ('action_type', '=', 'update'),
        ])
        
        self.assertGreater(new_count, initial_count)

    def test_log_deletion(self):
        """Test that deletions are logged."""
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': self.company.id,
        })
        
        partner_id = partner.id
        partner.unlink()
        
        # Check that deletion was logged
        log = self.Log.search([
            ('model_name', '=', 'res.partner'),
            ('record_id', '=', partner_id),
            ('action_type', '=', 'delete'),
        ], limit=1)
        
        self.assertTrue(log)

    def test_risk_score(self):
        """Test risk score calculation."""
        log = self.Log._log_action(
            action_type='delete',
            model_name='account.move',
            record_id=1,
            record_name='Test Invoice',
        )
        
        self.assertTrue(log)
        self.assertGreater(log.risk_score, 0)

    def test_severity_assessment(self):
        """Test severity assessment."""
        # High risk field
        severity = self.Log._assess_severity('res.users', 'password', 'old', 'new')
        self.assertEqual(severity, 'critical')
        
        # High risk model
        severity = self.Log._assess_severity('account.move', 'amount_total', '100', '200')
        self.assertEqual(severity, 'high')


class TestAuditTrailAlert(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Alert = self.env['audit.trail.alert']
        self.Log = self.env['audit.trail.log']

    def test_alert_creation(self):
        """Test alert creation."""
        alert = self.Alert.create({
            'name': 'Test Alert',
            'alert_type': 'bulk_delete',
            'threshold': 5,
            'time_window': 60,
            'severity': 'high',
        })
        
        self.assertTrue(alert)
        self.assertEqual(alert.state, 'active')

    def test_alert_activation(self):
        """Test alert activation/deactivation."""
        alert = self.Alert.create({
            'name': 'Test Alert',
            'alert_type': 'bulk_delete',
            'threshold': 5,
            'time_window': 60,
        })
        
        alert.action_deactivate()
        self.assertEqual(alert.state, 'inactive')
        
        alert.action_activate()
        self.assertEqual(alert.state, 'active')


class TestAuditTrailConfig(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Config = self.env['audit.trail.config']

    def test_get_config(self):
        """Test config retrieval."""
        config = self.Config.get_config()
        self.assertTrue(config)
        self.assertEqual(config.company_id, self.env.company)

    def test_reset_defaults(self):
        """Test config reset."""
        config = self.Config.get_config()
        config.write({'log_create': False})
        config.action_reset_defaults()
        config = self.Config.get_config()
        self.assertTrue(config.log_create)
