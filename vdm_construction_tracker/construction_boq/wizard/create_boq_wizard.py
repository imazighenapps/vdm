# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CreateBoqWizard(models.TransientModel):
    _name = 'create.boq.wizard'
    _description = 'Create BOQ Wizard'

    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
    )
    name = fields.Char(string='Reference')
    template_id = fields.Many2one(
        'construction.boq',
        string='Copy from Template',
        help='Copy lines from an existing BOQ',
    )

    def action_create_boq(self):
        vals = {
            'project_id': self.project_id.id,
            'name': self.name or 'New',
        }
        if self.template_id:
            boq = self.env['construction.boq'].create(vals)
            for line in self.template_id.line_ids:
                line.copy({'boq_id': boq.id})
            return {
                'type': 'ir.actions.act_window',
                'name': _('Bill of Quantities'),
                'res_model': 'construction.boq',
                'res_id': boq.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            boq = self.env['construction.boq'].create(vals)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Bill of Quantities'),
                'res_model': 'construction.boq',
                'res_id': boq.id,
                'view_mode': 'form',
                'target': 'current',
            }
