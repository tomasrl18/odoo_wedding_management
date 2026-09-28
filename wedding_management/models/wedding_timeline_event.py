# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WeddingTimelineEvent(models.Model):
    _name = "wedding.timeline.event"
    _description = "Wedding Timeline Event"
    _order = "wedding_id, start_time"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    start_time = fields.Datetime(string="Start Time", required=True)
    end_time = fields.Datetime(string="End Time", required=True)
    location = fields.Char(string="Location")
    notes = fields.Text(string="Notes")

    wedding_id = fields.Many2one(
        "wedding.event", string="Wedding", required=True, ondelete="cascade"
    )
    type_id = fields.Many2one(
        "wedding.timeline.type", string="Event Type", required=True
    )
    responsible_id = fields.Many2one("res.users", string="Responsible")

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("start_time", "end_time")
    def _check_times(self):
        for event in self:
            if event.end_time < event.start_time:
                raise ValidationError(
                    _(
                        "The end time of %(name)s cannot be before its "
                        "start time.",
                        name=event.type_id.name,
                    )
                )
