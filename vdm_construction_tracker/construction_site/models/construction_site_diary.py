# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConstructionSiteDiary(models.Model):
    _name = 'construction.site.diary'
    _description = 'Daily Progress Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )
    weather = fields.Selection([
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('stormy', 'Stormy'),
        ('snowy', 'Snowy'),
        ('windy', 'Windy'),
    ], string='Weather')
    temperature = fields.Float(string='Temperature (C)')
    work_completed = fields.Html(string='Work Completed')
    labor_deployed = fields.Integer(string='Labor Deployed')
    materials_used = fields.Text(string='Materials Used')
    machinery_used = fields.Text(string='Machinery Used')
    safety_issues = fields.Text(string='Safety Issues')
    delay_reasons = fields.Text(string='Delay Reasons')
    next_day_plan = fields.Text(string='Next Day Plan')
    engineer_remarks = fields.Text(string='Engineer Remarks')
    photo_ids = fields.One2many(
        'construction.site.photo',
        'diary_id',
        string='Photos',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True, copy=False)
    submitted_by = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )
    phase_ids = fields.Many2many(
        'construction.phase',
        string='Phases Worked Today',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('construction.site.diary') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        self.write({
            'state': 'submitted',
            'submitted_by': self.env.user.id,
        })

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
        })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_draft(self):
        self.write({'state': 'draft'})
