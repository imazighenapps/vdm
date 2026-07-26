# -*- coding: utf-8 -*-
from odoo import models, api


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        config = self.env['audit.trail.config'].sudo().get_config()
        if config and config.enable_logging and config.log_create:
            for record in records:
                model_name = record._name
                if model_name not in ('audit.trail.log', 'audit.trail.alert', 'audit.trail.config'):
                    self.env['audit.trail.log'].sudo().log_create(model_name, record)
        return records

    def write(self, vals):
        # Capture old values before write
        old_values = {}
        if self.env['audit.trail.config'].sudo().get_config().enable_logging:
            for record in self:
                old_values[record.id] = {}
                for field_name in vals.keys():
                    if hasattr(record, field_name):
                        old_values[record.id][field_name] = getattr(record, field_name, None)
        
        result = super().write(vals)
        
        # Log changes
        config = self.env['audit.trail.config'].sudo().get_config()
        if config and config.enable_logging and config.log_update:
            for record in self:
                model_name = record._name
                if model_name not in ('audit.trail.log', 'audit.trail.alert', 'audit.trail.config'):
                    self.env['audit.trail.log'].sudo().log_write(model_name, record, vals)
        
        return result

    def unlink(self):
        # Log deletion before unlink
        config = self.env['audit.trail.config'].sudo().get_config()
        if config and config.enable_logging and config.log_delete:
            for record in self:
                model_name = record._name
                if model_name not in ('audit.trail.log', 'audit.trail.alert', 'audit.trail.config'):
                    self.env['audit.trail.log'].sudo().log_unlink(model_name, record)
        
        return super().unlink()
