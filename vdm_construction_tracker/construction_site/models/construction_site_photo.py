# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionSitePhoto(models.Model):
    _name = 'construction.site.photo'
    _description = 'Site Photo'
    _order = 'photo_date desc, id desc'

    name = fields.Char(string='Caption')
    project_id = fields.Many2one(
        'construction.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    diary_id = fields.Many2one(
        'construction.site.diary',
        string='Daily Report',
        ondelete='set null',
    )
    phase_id = fields.Many2one(
        'construction.phase',
        string='Phase',
    )
    image = fields.Image(
        string='Photo',
        attachment=True,
        max_width=1920,
        max_height=1920,
    )
    image_medium = fields.Image(
        string='Medium Image',
        related='image',
        max_width=256,
        max_height=256,
    )
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    caption = fields.Char(string='Caption')
    photo_date = fields.Datetime(
        string='Photo Date',
        default=fields.Datetime.now,
    )
    photo_type = fields.Selection([
        ('progress', 'Progress'),
        ('quality', 'Quality Control'),
        ('safety', 'Safety'),
        ('issue', 'Issue'),
        ('general', 'General'),
    ], string='Photo Type', default='general')
    company_id = fields.Many2one(
        'res.company',
        related='project_id.company_id',
        store=True,
    )
