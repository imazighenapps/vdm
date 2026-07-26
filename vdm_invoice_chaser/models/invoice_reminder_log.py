from odoo import models, fields, api


class InvoiceReminderLog(models.Model):
    _name = 'invoice.reminder.log'
    _description = 'Invoice Reminder Log'
    _order = 'send_date desc, id'
    _rec_name = 'move_id'

    move_id = fields.Many2one('account.move', string='Invoice', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='move_id.partner_id', string='Customer', store=True)
    invoice_number = fields.Char(related='move_id.name', string='Invoice Number', store=True)

    level = fields.Selection([
        ('gentle', 'Gentle Reminder'),
        ('firm', 'Firm Reminder'),
        ('legal', 'Legal Notice'),
    ], string='Reminder Level', required=True)

    send_date = fields.Date(string='Send Date', required=True, default=fields.Date.context_today)
    send_uid = fields.Many2one('res.users', string='Sent By')

    amount_overdue = fields.Monetary(string='Amount Overdue', related='move_id.invoice_residual_signed')
    currency_id = fields.Many2one(related='move_id.currency_id')

    days_overdue = fields.Integer(related='move_id.days_overdue')

    notes = fields.Text(string='Notes')

    company_id = fields.Many2one(related='move_id.company_id', string='Company', store=True)
