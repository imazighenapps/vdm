# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import csv
import base64
from io import StringIO


class CbamWizardImport(models.TransientModel):
    _name = 'cbam.wizard.import'
    _description = 'CBAM Import Wizard'

    file = fields.Binary(string='CSV File', required=True)
    filename = fields.Char(string='Filename')
    sector = fields.Selection([
        ('cement', 'Cement'),
        ('steel', 'Iron & Steel'),
        ('aluminium', 'Aluminium'),
        ('fertilizer', 'Fertilizers'),
        ('electricity', 'Electricity'),
        ('hydrogen', 'Hydrogen'),
    ], string='Default Sector', required=True)
    import_date = fields.Date(string='Import Date', default=fields.Date.context_today)

    def action_import(self):
        if not self.file:
            raise ValidationError(_('Please select a CSV file.'))

        try:
            csv_data = base64.b64decode(self.file)
            csv_file = StringIO(csv_data.decode('utf-8'))
            reader = csv.DictReader(csv_file)

            events_vals = []
            for row in reader:
                product = self.env['product.product'].search([
                    ('name', '=', row.get('product_name', ''))
                ], limit=1)
                supplier = self.env['res.partner'].search([
                    ('name', '=', row.get('supplier_name', ''))
                ], limit=1)
                country = self.env['res.country'].search([
                    ('code', '=', row.get('country_code', ''))
                ], limit=1)

                if not product or not supplier or not country:
                    continue

                events_vals.append({
                    'product_id': product.id,
                    'supplier_id': supplier.id,
                    'origin_country_id': country.id,
                    'sector': self.sector,
                    'quantity': float(row.get('quantity', 0)),
                    'import_date': self.import_date,
                })

            if events_vals:
                self.env['cbam.import.event'].create(events_vals)

            return {
                'type': 'ir.actions.act_window_close',
                'info': _('Imported %d events successfully.') % len(events_vals),
            }
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(_('Error importing CSV: %s') % str(e))
