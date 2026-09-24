# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WeddingVendorBooking(models.Model):
    _name = "wedding.vendor.booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Wedding Vendor Booking"
    _order = "wedding_id, contract_date, id"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    description = fields.Char(string="Description")
    contract_date = fields.Date(string="Contract Date")
    amount_agreed = fields.Monetary(
        string="Agreed Amount", currency_field="currency_id"
    )
    advance_paid = fields.Monetary(
        string="Advance Paid", currency_field="currency_id"
    )
    payment_due_date = fields.Date(string="Payment Due Date")
    notes = fields.Text(string="Notes")

    partner_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, tracking=True
    )
    wedding_id = fields.Many2one(
        "wedding.event", string="Wedding", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        "res.company", related="wedding_id.company_id", store=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="wedding_id.company_id.currency_id", store=True
    )

    service_type = fields.Selection(
        [
            ("catering", "Catering"),
            ("photography", "Photography"),
            ("video", "Video"),
            ("music", "Music"),
            ("flowers", "Flowers"),
            ("decoration", "Decoration"),
            ("transport", "Transport"),
            ("accommodation", "Accommodation"),
            ("other", "Other"),
        ],
        string="Service Type",
        default="other",
        required=True,
    )
    state = fields.Selection(
        [
            ("proposal", "Proposal"),
            ("pending_confirmation", "Pending Confirmation"),
            ("contracted", "Contracted"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="proposal",
        required=True,
        tracking=True,
    )

    balance_due = fields.Monetary(
        string="Balance Due",
        help="Agreed amount minus advance paid.",
        currency_field="currency_id",
        compute="_compute_balance_due", store=True,
    )

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends("amount_agreed", "advance_paid")
    def _compute_balance_due(self):
        for booking in self:
            booking.balance_due = booking.amount_agreed - booking.advance_paid

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("amount_agreed", "advance_paid")
    def _check_amounts(self):
        for booking in self:
            if booking.amount_agreed < 0 or booking.advance_paid < 0:
                raise ValidationError(
                    _("Vendor booking amounts cannot be negative.")
                )
            if booking.advance_paid > booking.amount_agreed:
                raise ValidationError(
                    _(
                        "Advance paid (%(advance)s) cannot exceed the "
                        "agreed amount (%(agreed)s).",
                        advance=booking.advance_paid,
                        agreed=booking.amount_agreed,
                    )
                )
