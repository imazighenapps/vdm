from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCarbonTracker(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        
        self.config = self.env['esg.config'].create({
            'company_id': self.company.id,
            'base_year': 2024,
            'scope1_enabled': True,
            'scope2_enabled': True,
            'scope3_enabled': True,
        })
        
        self.emission_factor = self.env['esg.emission.factor'].create({
            'name': 'Test Factor',
            'code': 'TEST-EF-001',
            'scope': '1',
            'category': 'stationary_combustion',
            'fuel_type': 'natural_gas',
            'gas_type': 'co2',
            'gwp_value': 1.0,
            'factor_value': 2.044,
            'unit': 'kwh',
            'compute_method': 'physical',
            'source_database': 'custom',
        })
        
        self.inventory = self.env['esg.carbon.inventory'].create({
            'name': 'Test Inventory',
            'company_id': self.company.id,
            'period_start': '2024-01-01',
            'period_end': '2024-12-31',
            'period_type': 'yearly',
            'revenue_amount': 1000000,
            'employee_count': 50,
            'base_year_emissions': 100.0,
        })
    
    def test_emission_factor_creation(self):
        self.assertEqual(self.emission_factor.name, 'Test Factor')
        self.assertEqual(self.emission_factor.scope, '1')
        self.assertEqual(self.emission_factor.factor_value, 2.044)
    
    def test_emission_line_creation(self):
        emission_line = self.env['esg.emission.line'].create({
            'name': 'Test Emission',
            'inventory_id': self.inventory.id,
            'emission_factor_id': self.emission_factor.id,
            'quantity': 1000,
            'date': '2024-06-15',
        })
        
        self.assertEqual(emission_line.scope, '1')
        self.assertGreater(emission_line.emissions_kg, 0)
        self.assertGreater(emission_line.emissions_tco2e, 0)
    
    def test_inventory_totals(self):
        self.env['esg.emission.line'].create({
            'name': 'Test Emission 1',
            'inventory_id': self.inventory.id,
            'emission_factor_id': self.emission_factor.id,
            'quantity': 1000,
            'date': '2024-06-15',
        })
        
        self.inventory._compute_scope_totals()
        self.inventory._compute_total_emissions()
        
        self.assertGreater(self.inventory.total_emissions, 0)
    
    def test_carbon_offset(self):
        offset = self.env['esg.carbon.offset'].create({
            'name': 'Test Offset',
            'project_name': 'Test Project',
            'project_type': 'reforestation',
            'standard': 'gs',
            'total_credits': 50.0,
            'vintage_year': 2024,
            'purchase_date': '2024-06-15',
            'unit_price': 15.0,
        })
        
        self.assertEqual(offset.available_credits, 50.0)
        self.assertEqual(offset.total_cost, 750.0)
    
    def test_reduction_target(self):
        target = self.env['esg.reduction.target'].create({
            'name': 'Test Target',
            'company_id': self.company.id,
            'target_type': 'absolute',
            'scope': '1',
            'target_year': 2030,
            'base_year': 2024,
            'base_emissions': 100.0,
            'target_emissions': 50.0,
        })
        
        self.assertEqual(target.reduction_percentage, 50.0)
