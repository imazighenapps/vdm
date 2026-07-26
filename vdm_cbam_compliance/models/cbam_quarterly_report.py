# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import csv
import base64
from io import StringIO


class CbamQuarterlyReport(models.Model):
    _name = 'cbam.quarterly.report'
    _description = 'CBAM Quarterly Report'
    _order = 'year desc, quarter desc'

    name = fields.Char(string='Report Reference', required=True, copy=False, default='New')
    year = fields.Integer(string='Year', required=True, default=lambda self: fields.Date.context_today(self).year)
    quarter = fields.Selection([
        ('Q1', 'Q1 (Jan-Mar)'),
        ('Q2', 'Q2 (Apr-Jun)'),
        ('Q3', 'Q3 (Jul-Sep)'),
        ('Q4', 'Q4 (Oct-Dec)'),
    ], string='Quarter', required=True)
    import_event_ids = fields.One2many('cbam.import.event', 'quarterly_report_id', string='Import Events')
    total_imported_tonnes = fields.Float(string='Total Imported (tonnes)', compute='_compute_totals', store=True, digits=(16, 4))
    total_emissions = fields.Float(string='Total Emissions (tCO2e)', compute='_compute_totals', store=True, digits=(16, 4))
    certificate_surrender_ids = fields.One2many('cbam.certificate.surrender', 'quarterly_report_id', string='Certificate Surrenders')
    certificates_to_surrender = fields.Float(string='Certificates to Surrender', compute='_compute_totals', store=True, digits=(16, 2))
    certificates_balance = fields.Float(string='Certificate Balance', compute='_compute_totals', store=True, digits=(16, 2))
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('validated', 'Validated'),
        ('approved', 'Approved'),
    ], string='Status', default='draft')
    report_pdf = fields.Binary(string='Report PDF')
    report_filename = fields.Char(string='Report Filename')
    prepared_by = fields.Many2one('res.users', string='Prepared By')
    validated_by = fields.Many2one('res.users', string='Validated By')
    approved_by = fields.Many2one('res.users', string='Approved By')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('import_event_ids', 'import_event_ids.total_emissions', 'import_event_ids.quantity',
                 'certificate_surrender_ids', 'certificate_surrender_ids.quantity')
    def _compute_totals(self):
        for rec in self:
            rec.total_imported_tonnes = sum(rec.import_event_ids.mapped('quantity'))
            rec.total_emissions = sum(rec.import_event_ids.mapped('total_emissions'))
            surrendered = sum(rec.certificate_surrender_ids.mapped('quantity'))
            rec.certificates_to_surrender = surrendered
            available_certs = self.env['cbam.certificate'].search([
                ('status', 'in', ['available', 'partial']),
                ('company_id', '=', rec.company_id.id),
            ])
            total_available = sum(available_certs.mapped('remaining_quantity'))
            rec.certificates_balance = total_available - surrendered

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                year = vals.get('year', fields.Date.context_today(self).year)
                quarter = vals.get('quarter', 'Q1')
                vals['name'] = f"CBAM {quarter} {year}"
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            rec.write({'status': 'submitted', 'prepared_by': self.env.uid})

    def action_validate(self):
        for rec in self:
            rec.write({'status': 'validated', 'validated_by': self.env.uid})

    def action_approve(self):
        for rec in self:
            rec.write({'status': 'approved', 'approved_by': self.env.uid})

    def action_draft(self):
        for rec in self:
            rec.status = 'draft'

    def generate_csv_export(self):
        for rec in self:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'Import Reference', 'Product', 'Supplier', 'Country',
                'Sector', 'Quantity (tonnes)', 'Emission Factor',
                'Total Emissions (tCO2e)', 'Import Date'
            ])
            for event in rec.import_event_ids:
                writer.writerow([
                    event.name,
                    event.product_id.name,
                    event.supplier_id.name,
                    event.origin_country_id.name,
                    event.sector,
                    event.quantity,
                    event.emission_factor,
                    event.total_emissions,
                    event.import_date,
                ])
            csv_content = output.getvalue()
            output.close()
            rec.report_pdf = base64.b64encode(csv_content.encode('utf-8'))
            rec.report_filename = f"CBAM_{rec.quarter}_{rec.year}_export.csv"


class CbamSectorData(models.Model):
    _name = 'cbam.sector.data'
    _description = 'CBAM Sector Data'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    default_emission = fields.Float(string='Default Emission (tCO2e/t)', digits=(16, 6))


class CbamEmissionFactor(models.Model):
    _name = 'cbam.emission.factor'
    _description = 'CBAM Emission Factor'

    name = fields.Char(string='Name', required=True)
    gas_type = fields.Char(string='Gas Type', required=True)
    gwp = fields.Float(string='GWP (Global Warming Potential)', required=True)
