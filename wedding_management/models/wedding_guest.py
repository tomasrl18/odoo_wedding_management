# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WeddingGuest(models.Model):
    _name = "wedding.guest"
    _inherit = ["mail.thread"]
    _description = "Wedding Guest"
    _order = "wedding_id, name"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(string="Name", required=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    allowed_companions = fields.Integer(
        string="Allowed Companions", default=0
    )
    confirmed_companions = fields.Integer(
        string="Confirmed Companions", default=0
    )
    menu_choice = fields.Char(string="Menu Choice")
    notes = fields.Text(string="Notes")

    partner_id = fields.Many2one("res.partner", string="Contact")
    wedding_id = fields.Many2one(
        "wedding.event", string="Wedding", required=True, ondelete="cascade"
    )
    table_id = fields.Many2one("wedding.table", string="Table")

    invitation_state = fields.Selection(
        [
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("answered", "Answered"),
        ],
        string="Invitation Status",
        default="pending",
        required=True,
        tracking=True,
    )
    attendance_state = fields.Selection(
        [
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("declined", "Declined"),
        ],
        string="Attendance",
        default="pending",
        required=True,
        tracking=True,
    )

    actual_attendees = fields.Integer(
        string="Actual Attendees",
        help="The guest plus confirmed companions, only when attendance "
        "is confirmed. Zero otherwise.",
        compute="_compute_actual_attendees", store=True,
    )

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends("attendance_state", "confirmed_companions")
    def _compute_actual_attendees(self):
        for guest in self:
            if guest.attendance_state == "confirmed":
                guest.actual_attendees = 1 + guest.confirmed_companions
            else:
                guest.actual_attendees = 0

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("confirmed_companions", "allowed_companions")
    def _check_companions(self):
        for guest in self:
            if guest.confirmed_companions > guest.allowed_companions:
                raise ValidationError(
                    _(
                        "Confirmed companions (%(companions)s) cannot exceed "
                        "allowed companions (%(allowed)s) for guest %(name)s.",
                        companions=guest.confirmed_companions,
                        allowed=guest.allowed_companions,
                        name=guest.name,
                    )
                )

    @api.constrains("table_id")
    def _check_table_same_wedding(self):
        for guest in self:
            if guest.table_id and guest.table_id.wedding_id != guest.wedding_id:
                raise ValidationError(
                    _(
                        "Guest %(name)s cannot be assigned to a table of "
                        "another wedding.",
                        name=guest.name,
                    )
                )

    @api.constrains("table_id", "attendance_state")
    def _check_table_attendance(self):
        for guest in self:
            if guest.table_id and guest.attendance_state == "declined":
                raise ValidationError(
                    _(
                        "Guest %(name)s declined the invitation and cannot "
                        "be assigned to a table.",
                        name=guest.name,
                    )
                )
