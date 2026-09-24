# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WeddingTable(models.Model):
    _name = "wedding.table"
    _description = "Wedding Table"
    _order = "wedding_id, name"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(string="Table Name / Number", required=True)
    capacity = fields.Integer(string="Capacity", required=True, default=8)

    wedding_id = fields.Many2one(
        "wedding.event", string="Wedding", required=True, ondelete="cascade"
    )
    guest_ids = fields.One2many(
        "wedding.guest", "table_id", string="Assigned Guests"
    )

    occupancy = fields.Integer(
        string="Occupancy",
        help="Real attendees assigned to this table (companions included "
        "when attendance is confirmed).",
        compute="_compute_occupancy", store=True,
    )
    free_seats = fields.Integer(
        string="Free Seats", compute="_compute_occupancy", store=True
    )

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends("capacity", "guest_ids", "guest_ids.actual_attendees")
    def _compute_occupancy(self):
        for table in self:
            occupancy = sum(table.guest_ids.mapped("actual_attendees"))
            table.occupancy = occupancy
            table.free_seats = max(0, table.capacity - occupancy)

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("capacity")
    def _check_capacity(self):
        for table in self:
            if table.capacity <= 0:
                raise ValidationError(
                    _("The table capacity must be positive.")
                )
            if table.occupancy > table.capacity:
                raise ValidationError(
                    _(
                        "Table %(name)s is over capacity: %(occupancy)s "
                        "attendees for a capacity of %(capacity)s.",
                        name=table.name,
                        occupancy=table.occupancy,
                        capacity=table.capacity,
                    )
                )

    @api.constrains("guest_ids")
    def _check_guests(self):
        for table in self:
            for guest in table.guest_ids:
                if guest.wedding_id != table.wedding_id:
                    raise ValidationError(
                        _(
                            "Guest %(name)s belongs to another wedding and "
                            "cannot be assigned to table %(table)s.",
                            name=guest.name,
                            table=table.name,
                        )
                    )
                if guest.attendance_state == "declined":
                    raise ValidationError(
                        _(
                            "Guest %(name)s declined the invitation and "
                            "cannot be assigned to table %(table)s.",
                            name=guest.name,
                            table=table.name,
                        )
                    )
            if table.occupancy > table.capacity:
                raise ValidationError(
                    _(
                        "Table %(name)s is over capacity: %(occupancy)s "
                        "attendees for a capacity of %(capacity)s.",
                        name=table.name,
                        occupancy=table.occupancy,
                        capacity=table.capacity,
                    )
                )
