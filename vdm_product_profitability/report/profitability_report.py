# -*- coding: utf-8 -*-
from odoo import models, api


class ProfitabilityReport(models.AbstractModel):
    _name = 'report.vdm_product_profitability.report_profitability'
    _description = 'Profitability Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['product.profitability'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'product.profitability',
            'docs': docs,
            'data': data,
        }
