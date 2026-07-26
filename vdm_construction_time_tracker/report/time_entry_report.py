# -*- coding: utf-8 -*-
from odoo import models, api


class TimeEntryReport(models.AbstractModel):
    _name = 'report.vdm_construction_time_tracker.report_time_entry'
    _description = 'Time Entry Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['construction.time.entry'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'construction.time.entry',
            'docs': docs,
            'data': data,
        }
