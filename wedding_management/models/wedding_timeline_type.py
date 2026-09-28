# -*- coding: utf-8 -*-
from odoo import fields, models


class WeddingTimelineType(models.Model):
    _name = "wedding.timeline.type"
    _description = "Wedding Timeline Event Type"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(string="Event Name", required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The event type name already exists."),
    ]
