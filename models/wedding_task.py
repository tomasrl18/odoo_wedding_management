# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WeddingTask(models.Model):
    _name = "wedding.task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Wedding Task"
    _order = "wedding_id, due_date, id"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    due_date = fields.Date(string="Due Date")

    wedding_id = fields.Many2one(
        "wedding.event", string="Wedding", required=True, ondelete="cascade"
    )
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user,
    )

    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="1",
        required=True,
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("blocked", "Blocked"),
            ("done", "Done"),
        ],
        string="Status",
        default="pending",
        required=True,
        tracking=True,
    )

    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_is_overdue",
        store=True,
    )

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends("due_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for task in self:
            task.is_overdue = bool(
                task.due_date and task.state != "done" and task.due_date < today
            )
