# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TimeEntry(models.Model):
    _name = 'construction.time.entry'
    _description = 'Time Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'entry_date desc, id desc'

    name = fields.Char(string='Description', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, tracking=True, domain="[('allow_timesheets', '=', True)]")
    phase_id = fields.Many2one('construction.project.phase', string='Phase', tracking=True, domain="[('project_id', '=', project_id)]")
    worker_id = fields.Many2one('construction.worker', string='Worker', required=True, tracking=True)
    work_type = fields.Selection([
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('material', 'Material'),
        ('subcontract', 'Subcontract'),
    ], string='Work Type', default='labor', required=True, tracking=True)
    entry_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    start_time = fields.Float(string='Start Time', required=True, tracking=True)
    end_time = fields.Float(string='End Time', required=True, tracking=True)
    duration = fields.Float(string='Duration (hours)', compute='_compute_duration', store=True, tracking=True)
    hourly_rate = fields.Float(string='Hourly Rate', compute='_compute_hourly_rate', store=True, tracking=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    is_billable = fields.Boolean(string='Billable', default=True, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, tracking=True)
    invoice_status = fields.Selection([
        ('no', 'Not Invoiced'),
        ('pending', 'To Invoice'),
        ('invoiced', 'Invoiced'),
    ], string='Invoice Status', compute='_compute_invoice_status', store=True, tracking=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            if rec.end_time and rec.start_time:
                rec.duration = rec.end_time - rec.start_time
            else:
                rec.duration = 0.0

    @api.depends('worker_id', 'work_type')
    def _compute_hourly_rate(self):
        for rec in self:
            if rec.work_type == 'labor' and rec.worker_id:
                rec.hourly_rate = rec.worker_id.hourly_rate
            elif rec.work_type == 'equipment':
                rec.hourly_rate = self.env['ir.config_parameter'].sudo().get_param('construction_time_tracker.equipment_rate', 25.0)
            else:
                rec.hourly_rate = 0.0

    @api.depends('duration', 'hourly_rate')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.duration * rec.hourly_rate

    @api.depends('invoice_id')
    def _compute_invoice_status(self):
        for rec in self:
            if not rec.invoice_id:
                rec.invoice_status = 'no'
            elif rec.invoice_id.state == 'posted':
                rec.invoice_status = 'invoiced'
            else:
                rec.invoice_status = 'pending'

    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for rec in self:
            if rec.start_time < 0 or rec.start_time >= 24:
                raise ValidationError(_('Start time must be between 0 and 24.'))
            if rec.end_time < 0 or rec.end_time >= 24:
                raise ValidationError(_('End time must be between 0 and 24.'))
            if rec.end_time <= rec.start_time:
                raise ValidationError(_('End time must be after start time.'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_draft(self):
        self.write({'state': 'draft'})
