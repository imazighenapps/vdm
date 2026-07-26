from odoo import models, fields, api


class AiChatbotConversation(models.Model):
    _name = 'ai.chatbot.conversation'
    _description = 'AI Chatbot Conversation'
    _order = 'write_date desc'

    name = fields.Char(string='Conversation ID', required=True, copy=False)
    config_id = fields.Many2one('ai.chatbot.config', string='Chatbot Config', required=True)
    partner_id = fields.Many2one('res.partner', string='Contact')
    lead_id = fields.Many2one('crm.lead', string='CRM Lead')
    channel = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('website', 'Website'),
        ('telegram', 'Telegram'),
        ('other', 'Other'),
    ], string='Channel', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('waiting', 'Waiting for Human'),
        ('closed', 'Closed'),
    ], string='Status', default='active')
    contact_name = fields.Char(string='Contact Name')
    contact_phone = fields.Char(string='Phone')
    contact_email = fields.Char(string='Email')
    message_ids = fields.One2many('ai.chatbot.message', 'conversation_id', string='Messages')
    message_count = fields.Integer(string='Messages', compute='_compute_message_count')
    last_message = fields.Text(string='Last Message', compute='_compute_last_message')
    last_message_date = fields.Datetime(string='Last Message Date', compute='_compute_last_message')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    assigned_user_id = fields.Many2one('res.users', string='Assigned To')
    notes = fields.Text(string='Internal Notes')

    @api.depends('message_ids')
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    @api.depends('message_ids', 'message_ids.body', 'message_ids.timestamp')
    def _compute_last_message(self):
        for rec in self:
            if rec.message_ids:
                last_msg = rec.message_ids[-1]
                rec.last_message = last_msg.body
                rec.last_message_date = last_msg.timestamp
            else:
                rec.last_message = False
                rec.last_message_date = False

    @api.model_create_multi
    def create(self, vals_list):
        from datetime import datetime
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ai.chatbot.conversation') or datetime.now().strftime('CONV/%Y%m%d/%H%M%S')
        return super().create(vals_list)

    def action_send_bot_message(self, message_text):
        self.ensure_one()
        self.env['ai.chatbot.message'].create({
            'conversation_id': self.id,
            'body': message_text,
            'sender_type': 'bot',
        })

    def action_close(self):
        for rec in self:
            rec.status = 'closed'

    def action_escalate(self):
        for rec in self:
            rec.status = 'waiting'

    def action_reopen(self):
        for rec in self:
            rec.status = 'active'

    def create_lead(self):
        self.ensure_one()
        if self.lead_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'res_id': self.lead_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

        lead = self.env['crm.lead'].create({
            'name': f'Chatbot Lead - {self.contact_name or self.name}',
            'partner_id': self.partner_id.id if self.partner_id else False,
            'contact_name': self.contact_name,
            'phone': self.contact_phone,
            'email_from': self.contact_email,
            'description': self._get_conversation_summary(),
        })
        self.lead_id = lead.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_conversation_summary(self):
        messages = self.message_ids.sorted('timestamp')
        summary = "Conversation Summary:\n\n"
        for msg in messages:
            sender = "Bot" if msg.sender_type == 'bot' else "Customer"
            summary += f"[{sender}]: {msg.body}\n"
        return summary
