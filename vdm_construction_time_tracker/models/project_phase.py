# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectPhase(models.Model):
    _name = 'construction.project.phase'
    _description = 'Project Phase'
    _inherit = ['mail.thread']
    _order = 'sequence, id'

    name = fields.Char(string='Phase Name', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, tracking=True, domain="[('allow_timesheets', '=', True)]")
    sequence = fields.Integer(string='Sequence', default=10, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ], string='Status', default='planned', tracking=True)
    time_entry_ids = fields.One2many('construction.time.entry', 'phase_id', string='Time Entries')
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    progress = fields.Float(string='Progress %', default=0.0, tracking=True)

    @api.depends('time_entry_ids.duration')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = sum(rec.time_entry_ids.mapped('duration'))

    @api.depends('time_entry_ids.total_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.time_entry_ids.mapped('total_cost'))

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed', 'progress': 100.0})

    def action_hold(self):
        self.write({'state': 'on_hold'})

    def action_planned(self):
        self.write({'state': 'planned'})
