from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmissionImportWizard(models.TransientModel):
    _name = 'emission.import.wizard'
    _description = 'Emission Import Wizard'

    inventory_id = fields.Many2one('esg.carbon.inventory', string='Carbon Inventory', required=True)
    file_data = fields.Binary(string='Import File', required=True)
    file_name = fields.Char(string='File Name')
    import_format = fields.Selection([
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ], string='Import Format', default='csv', required=True)
    
    delimiter = fields.Selection([
        (',', 'Comma'),
        (';', 'Semicolon'),
        ('\t', 'Tab'),
    ], string='Delimiter', default=',')
    
    scope_filter = fields.Selection([
        ('all', 'All Scopes'),
        ('1', 'Scope 1 Only'),
        ('2', 'Scope 2 Only'),
        ('3', 'Scope 3 Only'),
    ], string='Scope Filter', default='all')
    
    def action_import(self):
        if not self.file_data:
            raise ValidationError("Please upload a file to import.")
        
        import base64
        file_content = base64.b64decode(self.file_data)
        
        lines = file_content.decode('utf-8').split('\n')
        if self.delimiter == ',':
            headers = lines[0].split(',')
        elif self.delimiter == ';':
            headers = lines[0].split(';')
        else:
            headers = lines[0].split('\t')
        
        imported_count = 0
        for line in lines[1:]:
            if not line.strip():
                continue
            
            if self.delimiter == ',':
                values = line.split(',')
            elif self.delimiter == ';':
                values = line.split(';')
            else:
                values = line.split('\t')
            
            if len(values) < 4:
                continue
            
            try:
                emission_line_vals = {
                    'inventory_id': self.inventory_id.id,
                    'name': values[0].strip() if values[0] else 'Imported Line',
                    'emission_factor_id': self._find_emission_factor(values[1].strip()),
                    'quantity': float(values[2].strip()) if values[2] else 1.0,
                    'date': self.inventory_id.period_start or fields.Date.today(),
                }
                
                self.env['esg.emission.line'].create(emission_line_vals)
                imported_count += 1
            except Exception as e:
                continue
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Complete',
                'message': f'Successfully imported {imported_count} emission lines.',
                'type': 'success',
            }
        }
    
    def _find_emission_factor(self, factor_name):
        factor = self.env['esg.emission.factor'].search([
            ('name', '=', factor_name),
            ('active', '=', True),
        ], limit=1)
        if not factor:
            factor = self.env['esg.emission.factor'].search([
                ('code', '=', factor_name),
                ('active', '=', True),
            ], limit=1)
        if not factor:
            raise ValidationError(f"Emission factor not found: {factor_name}")
        return factor.id
