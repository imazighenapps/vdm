# -*- coding: utf-8 -*-
from odoo import models, api


class AuditLogReport(models.AbstractModel):
    _name = 'report.audit_trail_pro.report_audit_log'
    _description = 'Audit Log Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['audit.trail.log'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'audit.trail.log',
            'docs': docs,
            'data': data,
        }
