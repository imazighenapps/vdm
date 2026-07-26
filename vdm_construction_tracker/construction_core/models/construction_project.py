# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConstructionProject(models.Model):
    _name = 'construction.project'
    _description = 'Construction Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    name = fields.Char(
        string='Project Name',
        required=True,
        tracking=True,
    )
    reference = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    sequence = fields.Integer(default=10)
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
    )
    site_manager_id = fields.Many2one(
        'hr.employee',
        string='Site Manager',
        tracking=True,
    )
    project_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
        ('renovation', 'Renovation'),
        ('other', 'Other'),
    ], string='Project Type', default='residential')
    contract_value = fields.Monetary(
        string='Contract Value',
        currency_field='currency_id',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
    )
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)

    # Computed fields
    progress = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True,
    )
    boq_count = fields.Integer(compute='_compute_counts')
    work_order_count = fields.Integer(compute='_compute_counts')
    billing_count = fields.Integer(compute='_compute_counts')
    expense_count = fields.Integer(compute='_compute_counts')
    photo_count = fields.Integer(compute='_compute_counts')
    diary_count = fields.Integer(compute='_compute_counts')
    change_order_count = fields.Integer(compute='_compute_counts')
    subcontract_count = fields.Integer(compute='_compute_counts')
    phase_count = fields.Integer(compute='_compute_counts')
    color = fields.Integer(string='Color Index')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Project name must be unique per company!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('construction.project') or 'New'
        return super().create(vals_list)

    @api.depends('phase_ids.progress', 'phase_ids.weight')
    def _compute_progress(self):
        for project in self:
            if project.phase_ids:
                total_weight = sum(project.phase_ids.mapped('weight'))
                if total_weight > 0:
                    project.progress = sum(
                        (p.progress * p.weight) / total_weight
                        for p in project.phase_ids
                    )
                else:
                    project.progress = 0.0
            else:
                project.progress = 0.0

    def _compute_counts(self):
        for project in self:
            project.boq_count = self.env['construction.boq'].search_count([
                ('project_id', '=', project.id)
            ])
            project.work_order_count = self.env['construction.work.order'].search_count([
                ('project_id', '=', project.id)
            ])
            project.billing_count = self.env['construction.ra.billing'].search_count([
                ('project_id', '=', project.id)
            ])
            project.expense_count = self.env['construction.expense'].search_count([
                ('project_id', '=', project.id)
            ])
            project.photo_count = self.env['construction.site.photo'].search_count([
                ('project_id', '=', project.id)
            ])
            project.diary_count = self.env['construction.site.diary'].search_count([
                ('project_id', '=', project.id)
            ])
            project.change_order_count = self.env['construction.change.order'].search_count([
                ('project_id', '=', project.id)
            ])
            project.subcontract_count = self.env['construction.subcontract'].search_count([
                ('project_id', '=', project.id)
            ])
            project.phase_count = self.env['construction.phase'].search_count([
                ('project_id', '=', project.id)
            ])

    # Phase relationship
    phase_ids = fields.One2many(
        'construction.phase',
        'project_id',
        string='Phases',
    )

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_hold(self):
        self.write({'state': 'on_hold'})

    def action_complete(self):
        self.write({'state': 'completed', 'progress': 100.0})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_view_boq(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bill of Quantities'),
            'res_model': 'construction.boq',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_work_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Work Orders'),
            'res_model': 'construction.work.order',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_billing(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('RA Billing'),
            'res_model': 'construction.ra.billing',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_expenses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expenses'),
            'res_model': 'construction.expense',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_photos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Site Photos'),
            'res_model': 'construction.site.photo',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_diaries(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Daily Progress Reports'),
            'res_model': 'construction.site.diary',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_change_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Change Orders'),
            'res_model': 'construction.change.order',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_subcontracts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Subcontracts'),
            'res_model': 'construction.subcontract',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_phases(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Phases'),
            'res_model': 'construction.phase',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
