# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WeddingEvent(models.Model):
    _name = "wedding.event"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Wedding Event"
    _order = "date asc"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(string="Wedding Name", required=True, tracking=True)
    date = fields.Datetime(string="Date & Time", required=True, tracking=True)
    venue = fields.Char(string="Venue", tracking=True)
    target_budget = fields.Monetary(
        string="Target Budget", currency_field="currency_id"
    )
    expected_guests = fields.Integer(string="Expected Guests")

    partner_1_id = fields.Many2one(
        "res.partner", string="Partner 1", required=True, tracking=True
    )
    partner_2_id = fields.Many2one(
        "res.partner", string="Partner 2", required=True, tracking=True
    )
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True
    )

    guest_ids = fields.One2many("wedding.guest", "wedding_id", string="Guests")
    table_ids = fields.One2many("wedding.table", "wedding_id", string="Tables")
    vendor_booking_ids = fields.One2many(
        "wedding.vendor.booking", "wedding_id", string="Vendor Bookings"
    )
    budget_line_ids = fields.One2many(
        "wedding.budget.line", "wedding_id", string="Budget Lines"
    )
    task_ids = fields.One2many("wedding.task", "wedding_id", string="Tasks")
    timeline_event_ids = fields.One2many(
        "wedding.timeline.event", "wedding_id", string="Timeline Events"
    )

    guest_count = fields.Integer(
        string="Guests Count", compute="_compute_guest_count", store=True
    )
    table_count = fields.Integer(
        string="Tables Count", compute="_compute_table_count", store=True
    )
    vendor_count = fields.Integer(
        string="Vendors Count", compute="_compute_vendor_count", store=True
    )
    budget_line_count = fields.Integer(
        string="Budget Lines Count", compute="_compute_budget_line_count", store=True
    )
    task_count = fields.Integer(
        string="Tasks Count", compute="_compute_task_count", store=True
    )
    confirmed_guests = fields.Integer(
        string="Confirmed Guests",
        help="Real attendees of confirmed guests (companions included).",
        compute="_compute_guests_summary", store=True,
    )
    pending_guests = fields.Integer(
        string="Pending Guests", compute="_compute_guests_summary", store=True
    )
    pending_tasks = fields.Integer(
        string="Pending Tasks", compute="_compute_pending_tasks", store=True
    )
    estimated_budget = fields.Monetary(
        string="Estimated Budget", currency_field="currency_id",
        compute="_compute_estimated_budget", store=True,
    )
    actual_spend = fields.Monetary(
        string="Actual Spend", currency_field="currency_id",
        compute="_compute_actual_spend", store=True,
    )
    budget_diff = fields.Monetary(
        string="Budget Difference",
        help="Target budget minus actual spend.",
        currency_field="currency_id",
        compute="_compute_budget_diff", store=True,
    )
    budget_usage_pct = fields.Float(
        string="Budget Usage (%)", compute="_compute_budget_usage_pct", store=True
    )
    table_occupancy_pct = fields.Float(
        string="Table Occupancy (%)", compute="_compute_table_occupancy_pct", store=True
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planning", "Planning"),
            ("confirmed", "Confirmed"),
            ("done", "Celebrated"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends("guest_ids")
    def _compute_guest_count(self):
        for wedding in self:
            wedding.guest_count = len(wedding.guest_ids)

    @api.depends("table_ids")
    def _compute_table_count(self):
        for wedding in self:
            wedding.table_count = len(wedding.table_ids)

    @api.depends("vendor_booking_ids")
    def _compute_vendor_count(self):
        for wedding in self:
            wedding.vendor_count = len(wedding.vendor_booking_ids)

    @api.depends("budget_line_ids")
    def _compute_budget_line_count(self):
        for wedding in self:
            wedding.budget_line_count = len(wedding.budget_line_ids)

    @api.depends("task_ids")
    def _compute_task_count(self):
        for wedding in self:
            wedding.task_count = len(wedding.task_ids)

    @api.depends("guest_ids.attendance_state", "guest_ids.actual_attendees")
    def _compute_guests_summary(self):
        for wedding in self:
            confirmed = wedding.guest_ids.filtered(
                lambda g: g.attendance_state == "confirmed"
            )
            wedding.confirmed_guests = sum(confirmed.mapped("actual_attendees"))
            wedding.pending_guests = len(
                wedding.guest_ids.filtered(
                    lambda g: g.attendance_state == "pending"
                )
            )

    @api.depends("task_ids.state")
    def _compute_pending_tasks(self):
        for wedding in self:
            wedding.pending_tasks = len(
                wedding.task_ids.filtered(lambda t: t.state != "done")
            )

    @api.depends("budget_line_ids.estimated_amount")
    def _compute_estimated_budget(self):
        for wedding in self:
            wedding.estimated_budget = sum(
                wedding.budget_line_ids.mapped("estimated_amount")
            )

    @api.depends("budget_line_ids.actual_amount")
    def _compute_actual_spend(self):
        for wedding in self:
            wedding.actual_spend = sum(
                wedding.budget_line_ids.mapped("actual_amount")
            )

    @api.depends("target_budget", "actual_spend")
    def _compute_budget_diff(self):
        for wedding in self:
            wedding.budget_diff = wedding.target_budget - wedding.actual_spend

    @api.depends("target_budget", "actual_spend")
    def _compute_budget_usage_pct(self):
        for wedding in self:
            if wedding.target_budget > 0:
                wedding.budget_usage_pct = (
                    wedding.actual_spend / wedding.target_budget * 100.0
                )
            else:
                wedding.budget_usage_pct = 0.0

    @api.depends("table_ids.occupancy", "table_ids.capacity")
    def _compute_table_occupancy_pct(self):
        for wedding in self:
            capacity = sum(wedding.table_ids.mapped("capacity"))
            if capacity > 0:
                wedding.table_occupancy_pct = (
                    sum(wedding.table_ids.mapped("occupancy")) / capacity * 100.0
                )
            else:
                wedding.table_occupancy_pct = 0.0

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("partner_1_id", "partner_2_id")
    def _check_partners_distinct(self):
        for wedding in self:
            if (
                wedding.partner_1_id
                and wedding.partner_2_id
                and wedding.partner_1_id == wedding.partner_2_id
            ):
                raise ValidationError(
                    _("The two partners of the wedding must be different.")
                )

    @api.constrains("date")
    def _check_date(self):
        for wedding in self:
            if wedding.date and wedding.date < fields.Datetime.now():
                raise ValidationError(
                    _("The wedding date cannot be in the past.")
                )
