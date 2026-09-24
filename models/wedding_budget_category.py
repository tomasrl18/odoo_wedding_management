# -*- coding: utf-8 -*-
from odoo import fields, models


class WeddingBudgetCategory(models.Model):
    _name = "wedding.budget.category"
    _description = "Wedding Budget Category"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(string="Category Name", required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The category name already exists."),
    ]
