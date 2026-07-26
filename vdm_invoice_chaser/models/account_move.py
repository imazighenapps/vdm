from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    reminder_count = fields.Integer(string='Reminders Sent', compute='_compute_reminder_count')
    last_reminder_date = fields.Date(string='Last Reminder Date', compute='_compute_last_reminder')
    days_overdue = fields.Integer(string='Days Overdue', compute='_compute_days_overdue')
    reminder_level = fields.Selection([
        ('none', 'None'),
        ('gentle', 'Gentle'),
        ('firm', 'Firm'),
        ('legal', 'Legal'),
    ], string='Reminder Level', compute='_compute_reminder_level')

    @api.depends('invoice_line_ids')
    def _compute_reminder_count(self):
        for move in self:
            logs = self.env['invoice.reminder.log'].search([('move_id', '=', move.id)])
            move.reminder_count = len(logs)

    def _compute_last_reminder(self):
        for move in self:
            log = self.env['invoice.reminder.log'].search([
                ('move_id', '=', move.id)
            ], order='send_date desc', limit=1)
            move.last_reminder_date = log.send_date if log else False

    def _compute_days_overdue(self):
        today = fields.Date.today()
        for move in self:
            if move.invoice_date_due and move.invoice_date_due < today and move.state == 'posted' and move.payment_state != 'paid':
                delta = today - move.invoice_date_due
                move.days_overdue = delta.days
            else:
                move.days_overdue = 0

    def _compute_reminder_level(self):
        for move in self:
            if move.days_overdue >= 60:
                move.reminder_level = 'legal'
            elif move.days_overdue >= 30:
                move.reminder_level = 'firm'
            elif move.days_overdue >= 7:
                move.reminder_level = 'gentle'
            else:
                move.reminder_level = 'none'

    def action_send_reminder(self):
        self.ensure_one()
        template = self._get_reminder_template()
        if template:
            template.send_mail(self.id, force_send=True)
            self.env['invoice.reminder.log'].create({
                'move_id': self.id,
                'level': self.reminder_level,
                'send_date': fields.Date.today(),
                'send_uid': self.env.uid,
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Reminder Sent',
                    'message': f'Reminder sent to {self.partner_id.name}',
                    'type': 'success',
                }
            }

    def action_send_all_overdue(self):
        overdue = self.search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', fields.Date.today()),
        ])
        sent_count = 0
        for inv in overdue:
            if inv.invoice_residual_signed >= (self.env.company.chaser_min_amount or 100):
                template = inv._get_reminder_template()
                if template:
                    template.send_mail(inv.id, force_send=True)
                    self.env['invoice.reminder.log'].create({
                        'move_id': inv.id,
                        'level': inv.reminder_level,
                        'send_date': fields.Date.today(),
                        'send_uid': self.env.uid,
                    })
                    sent_count += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bulk Reminders Sent',
                'message': f'{sent_count} reminders sent to overdue customers.',
                'type': 'success',
            }
        }

    def _get_reminder_template(self):
        level = self.reminder_level
        templates = {
            'gentle': 'vdm_invoice_chaser.email_template_reminder_gentle',
            'firm': 'vdm_invoice_chaser.email_template_reminder_firm',
            'legal': 'vdm_invoice_chaser.email_template_reminder_legal',
        }
        template_ref = templates.get(level)
        if template_ref:
            return self.env.ref(template_ref)
        return self.env.ref('vdm_invoice_chaser.email_template_reminder_gentle')

    def action_view_reminder_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reminder History',
            'res_model': 'invoice.reminder.log',
            'view_mode': 'list,form',
            'domain': [('move_id', '=', self.id)],
            'context': {'default_move_id': self.id},
        }
