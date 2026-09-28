# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WeddingBudgetLine(models.Model):
    _name = "wedding.budget.line"
    _description = "Wedding Budget Line"
    _order = "wedding_id, category_id, id"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    description = fields.Char(string="Description")
    estimated_amount = fields.Monetary(
        string="Estimated Amount", currency_field="currency_id"
    )
    actual_amount = fields.Monetary(
        string="Actual Amount", currency_field="currency_id"
    )

    wedding_id = fields.Many2one(
        "wedding.event", string="Wedding", required=True, ondelete="cascade"
    )
    category_id = fields.Many2one(
        "wedding.budget.category", string="Category", required=True
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    company_id = fields.Many2one(
        "res.company", related="wedding_id.company_id", store=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="wedding_id.company_id.currency_id", store=True
    )

    payment_state = fields.Selection(
        [
            ("unpaid", "Unpaid"),
            ("partial", "Partially Paid"),
            ("paid", "Paid"),
        ],
        string="Payment Status",
        default="unpaid",
        required=True,
    )

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("estimated_amount", "actual_amount")
    def _check_amounts(self):
        for line in self:
            if line.estimated_amount < 0 or line.actual_amount < 0:
                raise ValidationError(
                    _("Budget amounts cannot be negative.")
                )
