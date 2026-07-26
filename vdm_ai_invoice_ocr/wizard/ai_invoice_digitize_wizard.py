from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class AiInvoiceDigitizeWizard(models.TransientModel):
    _name = 'ai.invoice.digitize.wizard'
    _description = 'AI Invoice Digitization Wizard'

    invoice_id = fields.Many2one('account.move', string='Invoice', required=True)
    config_id = fields.Many2one('ai.invoice.config', string='AI Configuration',
        default=lambda self: self.env['ai.invoice.config'].search([('active', '=', True)], limit=1))
    provide_file = fields.Boolean(string='Provide New File', default=False)
    file = fields.Binary(string='Invoice File')
    filename = fields.Char(string='Filename')

    extraction_done = fields.Boolean(string='Extraction Done', default=False)
    invoice_number = fields.Char(string='Invoice Number')
    invoice_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    vendor_name = fields.Char(string='Vendor Name')
    total_amount = fields.Float(string='Total Amount')
    subtotal = fields.Float(string='Subtotal')
    tax_amount = fields.Float(string='Tax Amount')
    currency = fields.Char(string='Currency', default='EUR')
    validation_errors = fields.Text(string='Validation Warnings')
    extracted_data_json = fields.Text(string='Extracted Data (JSON)')

    def action_digitize(self):
        self.ensure_one()
        if not self.config_id:
            raise UserError(_('Please select an AI configuration.'))

        digitize_engine = self.env['ai.invoice.digitize']

        file_content = False
        if self.provide_file and self.file:
            file_content = self.file

        try:
            extracted_data = digitize_engine.digitize_invoice(
                self.invoice_id,
                file_content=file_content,
            )
        except Exception as e:
            raise UserError(_('Extraction failed: %s') % str(e))

        self.write({
            'extraction_done': True,
            'invoice_number': extracted_data.get('invoice_number', ''),
            'invoice_date': extracted_data.get('invoice_date', False),
            'due_date': extracted_data.get('due_date', False),
            'vendor_name': extracted_data.get('vendor_name', ''),
            'total_amount': extracted_data.get('total_amount', 0.0),
            'subtotal': extracted_data.get('subtotal', 0.0),
            'tax_amount': extracted_data.get('tax_amount', 0.0),
            'currency': extracted_data.get('currency', 'EUR'),
            'extracted_data_json': str(extracted_data),
        })

        errors = digitize_engine._validate_extraction(extracted_data)
        if errors:
            self.validation_errors = '\n'.join(errors)
        else:
            self.validation_errors = 'No validation warnings.'

    def action_apply(self):
        self.ensure_one()
        if not self.extraction_done:
            raise UserError(_('No extraction data available.'))

        import ast
        try:
            extracted_data = ast.literal_eval(self.extracted_data_json)
        except Exception:
            extracted_data = {
                'invoice_number': self.invoice_number,
                'invoice_date': self.invoice_date,
                'due_date': self.due_date,
                'vendor_name': self.vendor_name,
                'total_amount': self.total_amount,
                'subtotal': self.subtotal,
                'tax_amount': self.tax_amount,
                'currency': self.currency,
            }

        digitize_engine = self.env['ai.invoice.digitize']
        digitize_engine.apply_extraction(self.invoice_id, extracted_data)

        return {
            'type': 'ir.actions.act_window_close',
            'info': 'Invoice digitized successfully.',
        }
