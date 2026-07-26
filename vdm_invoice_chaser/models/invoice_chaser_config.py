from odoo import models, fields, api


class InvoiceChaserConfig(models.Model):
    _name = 'invoice.chaser.config'
    _description = 'Invoice Chaser Configuration'
    _inherits = {'res.company': 'company_id'}

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade')

    enabled = fields.Boolean(string='Enable Auto Reminders', default=True)

    reminder_j7 = fields.Boolean(string='Reminder at J+7', default=True)
    reminder_j15 = fields.Boolean(string='Reminder at J+15', default=True)
    reminder_j30 = fields.Boolean(string='Reminder at J+30', default=True)
    reminder_j60 = fields.Boolean(string='Reminder at J+60', default=True)

    min_amount = fields.Float(string='Minimum Amount for Reminders', default=100.0)
    currency_id = fields.Many2one('res.currency', string='Currency')

    escalate_manager = fields.Boolean(string='Escalate to Manager', default=True)
    escalate_threshold = fields.Float(string='Escalate if amount > (€)', default=10000.0)

    manager_user_id = fields.Many2one('res.users', string='Escalation Manager')

    auto_send = fields.Boolean(string='Auto-Send Reminders', default=False,
        help='If enabled, reminders are sent automatically. If disabled, only logged.')
