import json
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AiInvoiceDigitize(models.AbstractModel):
    _name = 'ai.invoice.digitize'
    _description = 'AI Invoice Digitization Engine'

    def _get_config(self, company_id=False):
        domain = [('active', '=', True)]
        if company_id:
            domain.append(('company_id', '=', company_id))
        config = self.env['ai.invoice.config'].search(domain, limit=1)
        if not config:
            raise UserError(_('No active AI Invoice configuration found. Please configure one in Settings.'))
        return config

    def _build_extraction_prompt(self, config, ocr_text=False):
        base_context = {
            'guided': self._get_full_context(config),
            'simplified': self._get_taxes_only_context(config),
            'free': '',
        }

        prompt = f"""Extract invoice data from the following document. Return a JSON object with the following fields:
        {{
            "invoice_number": "string",
            "invoice_date": "YYYY-MM-DD",
            "due_date": "YYYY-MM-DD",
            "vendor_name": "string",
            "vendor_vat": "string",
            "vendor_email": "string",
            "total_amount": 0.0,
            "subtotal": 0.0,
            "tax_amount": 0.0,
            "currency": "EUR",
            "payment_terms": "string",
            "lines": [
                {{
                    "description": "string",
                    "quantity": 0.0,
                    "unit_price": 0.0,
                    "tax_rate": 0.0,
                    "amount": 0.0
                }}
            ]
        }}

        {base_context.get(config.extraction_mode, '')}

        Document text:
        {ocr_text}

        Return ONLY the JSON object, no additional text."""

        return prompt

    def _get_full_context(self, config):
        company = config.company_id or self.env.company
        accounts = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('account_type', '=', 'expense'),
        ], limit=20)

        taxes = self.env['account.tax'].search([
            ('company_id', '=', company.id),
            ('type_tax_use', '=', 'purchase'),
        ], limit=20)

        account_list = '\n'.join([f"- {a.code}: {a.name}" for a in accounts])
        tax_list = '\n'.join([f"- {t.amount}%: {t.name}" for t in taxes])

        return f"""
        Available accounts (match invoice lines to these):
        {account_list}

        Available taxes:
        {tax_list}
        """

    def _get_taxes_only_context(self, config):
        company = config.company_id or self.env.company
        taxes = self.env['account.tax'].search([
            ('company_id', '=', company.id),
            ('type_tax_use', '=', 'purchase'),
        ], limit=20)

        tax_list = '\n'.join([f"- {t.amount}%: {t.name}" for t in taxes])
        return f"Match taxes to these rates:\n{tax_list}"

    def _call_ai_provider(self, config, prompt):
        import urllib.request
        import urllib.error

        provider_config = config.get_provider_config()
        if not provider_config:
            raise UserError(_('Invalid AI provider configuration.'))

        api_url = provider_config['api_url']
        headers = provider_config['headers']

        if config.provider in ('openai', 'deepseek', 'mistral'):
            payload = json.dumps({
                'model': config.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': config.max_tokens,
                'temperature': config.temperature,
            }).encode('utf-8')
        elif config.provider == 'anthropic':
            payload = json.dumps({
                'model': config.model,
                'max_tokens': config.max_tokens,
                'messages': [{'role': 'user', 'content': prompt}],
            }).encode('utf-8')
        elif config.provider == 'google':
            url_params = provider_config.get('params', {})
            api_url += '?' + '&'.join([f'{k}={v}' for k, v in url_params.items()])
            payload = json.dumps({
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'maxOutputTokens': config.max_tokens,
                    'temperature': config.temperature,
                },
            }).encode('utf-8')
        else:
            raise UserError(_('Unsupported provider: %s') % config.provider)

        try:
            req = urllib.request.Request(api_url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))

            if config.provider in ('openai', 'deepseek', 'mistral'):
                choices = result.get('choices', [])
                if choices:
                    return choices[0].get('message', {}).get('content', '')
                return ''
            elif config.provider == 'anthropic':
                content = result.get('content', [])
                if content:
                    return content[0].get('text', '')
                return ''
            elif config.provider == 'google':
                candidates = result.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return parts[0].get('text', '')
                return ''
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            _logger.error('AI Provider error: %s', error_body)
            raise UserError(_('AI Provider error: %s\n%s') % (e.code, error_body))
        except Exception as e:
            _logger.error('AI extraction failed: %s', str(e))
            raise UserError(_('AI extraction failed: %s') % str(e))

    def _validate_extraction(self, data):
        errors = []

        if data.get('subtotal') and data.get('tax_amount') and data.get('total_amount'):
            expected_total = data['subtotal'] + data['tax_amount']
            if abs(expected_total - data['total_amount']) > 0.01:
                errors.append('Total mismatch: subtotal + tax != total')

        if data.get('lines'):
            line_total = sum(l.get('amount', 0) for l in data['lines'])
            if data.get('subtotal') and abs(line_total - data['subtotal']) > 0.01:
                errors.append('Line items total mismatch with subtotal')

        if data.get('due_date') and data.get('invoice_date'):
            if data['due_date'] < data['invoice_date']:
                errors.append('Due date is before invoice date')

        return errors

    def _learn_from_correction(self, config, invoice_id, field_name, old_value, new_value):
        if not config.learning_enabled:
            return

        vendor_memory = self.env['ai.vendor.memory']
        if invoice_id.partner_id:
            memory = vendor_memory.search([
                ('partner_id', '=', invoice_id.partner_id.id),
                ('field_name', '=', field_name),
            ], limit=1)

            if memory:
                memory.write({
                    'corrected_value': str(new_value),
                    'correction_count': memory.correction_count + 1,
                })
            else:
                vendor_memory.create({
                    'partner_id': invoice_id.partner_id.id,
                    'field_name': field_name,
                    'original_value': str(old_value),
                    'corrected_value': str(new_value),
                    'correction_count': 1,
                })

    def digitize_invoice(self, invoice_id, file_content=False, file_name=False):
        config = self._get_config(invoice_id.company_id.id)

        ocr_text = file_content
        if not ocr_text and invoice_id.attachment_ids:
            for attachment in invoice_id.attachment_ids:
                if attachment.mimetype and 'pdf' in attachment.mimetype:
                    ocr_text = attachment.datas
                    break

        if not ocr_text:
            raise UserError(_('No document content available for extraction.'))

        prompt = self._build_extraction_prompt(config, ocr_text)
        response = self._call_ai_provider(config, prompt)

        try:
            clean_response = response.strip()
            if clean_response.startswith('```'):
                clean_response = clean_response.split('\n', 1)[1]
            if clean_response.endswith('```'):
                clean_response = clean_response.rsplit('```', 1)[0]
            clean_response = clean_response.strip()

            extracted_data = json.loads(clean_response)
        except json.JSONDecodeError:
            raise UserError(_('Failed to parse AI response as JSON. Please try again.'))

        errors = self._validate_extraction(extracted_data)
        if errors:
            _logger.warning('Validation warnings: %s', errors)

        return extracted_data

    def apply_extraction(self, invoice_id, extracted_data):
        invoice_id.ensure_one()

        if extracted_data.get('vendor_name'):
            vendor = self.env['res.partner'].search([
                ('name', 'ilike', extracted_data['vendor_name']),
            ], limit=1)
            if vendor:
                invoice_id.write({'partner_id': vendor.id})

        vals = {}
        if extracted_data.get('invoice_number'):
            vals['ref'] = extracted_data['invoice_number']
        if extracted_data.get('invoice_date'):
            vals['invoice_date'] = extracted_data['invoice_date']
        if extracted_data.get('due_date'):
            vals['invoice_date_due'] = extracted_data['due_date']
        if extracted_data.get('total_amount'):
            vals['amount_total'] = extracted_data['total_amount']

        if vals:
            invoice_id.write(vals)

        if extracted_data.get('lines'):
            config = self._get_config(invoice_id.company_id.id)
            if config.extract_lines:
                self._apply_invoice_lines(invoice_id, extracted_data['lines'])

        return True

    def _apply_invoice_lines(self, invoice_id, lines):
        invoice_id.invoice_line_ids.unlink()

        for line_data in lines:
            vals = {
                'name': line_data.get('description', ''),
                'quantity': line_data.get('quantity', 1.0),
                'price_unit': line_data.get('unit_price', 0.0),
            }

            if line_data.get('tax_rate'):
                tax = self.env['account.tax'].search([
                    ('amount', '=', line_data['tax_rate']),
                    ('company_id', '=', invoice_id.company_id.id),
                    ('type_tax_use', '=', 'purchase'),
                ], limit=1)
                if tax:
                    vals['tax_ids'] = [(6, 0, [tax.id])]

            self.env['account.move.line'].create({
                **vals,
                'move_id': invoice_id.id,
            })
