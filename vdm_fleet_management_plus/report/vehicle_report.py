# -*- coding: utf-8 -*-
from odoo import models, api


class VehicleReport(models.AbstractModel):
    _name = 'report.vdm_fleet_management_plus.report_vehicle'
    _description = 'Vehicle Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['fleet.vehicle.plus'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'fleet.vehicle.plus',
            'docs': docs,
            'data': data,
        }
