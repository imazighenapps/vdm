# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Worker(models.Model):
    _name = 'construction.worker'
    _description = 'Construction Worker'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='Worker Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    worker_type = fields.Selection([
        ('employee', 'Employee'),
        ('contractor', 'Contractor'),
        ('subcontractor', 'Subcontractor'),
    ], string='Worker Type', default='employee', required=True, tracking=True)
    hourly_rate = fields.Float(string='Hourly Rate', required=True, tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    skill_ids = fields.Many2many('construction.worker.skill', string='Skills')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    time_entry_ids = fields.One2many('construction.time.entry', 'worker_id', string='Time Entries')
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)

    @api.depends('time_entry_ids.duration')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = sum(rec.time_entry_ids.mapped('duration'))

    @api.depends('time_entry_ids.total_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.time_entry_ids.mapped('total_cost'))


class WorkerSkill(models.Model):
    _name = 'construction.worker.skill'
    _description = 'Worker Skill'

    name = fields.Char(string='Skill Name', required=True)
    description = fields.Text(string='Description')
