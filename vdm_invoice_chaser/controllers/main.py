from odoo import http
from odoo.http import request


class InvoiceChaserController(http.Controller):

    @http.route('/invoice_chaser/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        company = request.env.company
        today = request.Date.today()

        invoices = request.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', today),
        ])

        total_overdue = sum(invoices.mapped('invoice_residual_signed'))
        count_overdue = len(invoices)
        count_j7 = len(invoices.filtered(lambda i: 7 <= i.days_overdue < 15))
        count_j15 = len(invoices.filtered(lambda i: 15 <= i.days_overdue < 30))
        count_j30 = len(invoices.filtered(lambda i: 30 <= i.days_overdue < 60))
        count_j60 = len(invoices.filtered(lambda i: i.days_overdue >= 60))

        amount_j7 = sum(invoices.filtered(lambda i: 7 <= i.days_overdue < 15).mapped('invoice_residual_signed'))
        amount_j15 = sum(invoices.filtered(lambda i: 15 <= i.days_overdue < 30).mapped('invoice_residual_signed'))
        amount_j30 = sum(invoices.filtered(lambda i: 30 <= i.days_overdue < 60).mapped('invoice_residual_signed'))
        amount_j60 = sum(invoices.filtered(lambda i: i.days_overdue >= 60).mapped('invoice_residual_signed'))

        top_overdue = []
        partners = invoices.mapped('partner_id')
        for partner in partners[:10]:
            partner_invoices = invoices.filtered(lambda i: i.partner_id == partner)
            top_overdue.append({
                'partner': partner.name,
                'count': len(partner_invoices),
                'amount': sum(partner_invoices.mapped('invoice_residual_signed')),
                'max_days': max(partner_invoices.mapped('days_overdue')) if partner_invoices else 0,
            })
        top_overdue.sort(key=lambda x: x['amount'], reverse=True)

        recent_logs = request.env['invoice.reminder.log'].search([], order='send_date desc', limit=10)
        logs_data = [{
            'invoice': log.invoice_number,
            'partner': log.partner_id.name,
            'level': log.level,
            'date': log.send_date.strftime('%Y-%m-%d') if log.send_date else '',
        } for log in recent_logs]

        return {
            'summary': {
                'total_overdue': total_overdue,
                'count_overdue': count_overdue,
                'count_j7': count_j7,
                'count_j15': count_j15,
                'count_j30': count_j30,
                'count_j60': count_j60,
                'amount_j7': amount_j7,
                'amount_j15': amount_j15,
                'amount_j30': amount_j30,
                'amount_j60': amount_j60,
            },
            'top_overdue': top_overdue,
            'recent_logs': logs_data,
        }
