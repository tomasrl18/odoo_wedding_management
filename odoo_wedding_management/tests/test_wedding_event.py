# -*- coding: utf-8 -*-
"""Tests for wedding.event: creation, states and summary computations."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_wedding_event", "all", "wedding_management")
class TestWeddingEvent(TestWeddingSetup):

    def test_create_wedding(self):
        wedding = self.Wedding.create({
            "name": "New Wedding",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=10),
        })
        self.assertTrue(wedding.id)
        self.assertEqual(wedding.state, "draft")
        self.assertEqual(wedding.name, "New Wedding")

    def test_same_partner_rejected(self):
        with self.assertRaises(ValidationError):
            self.Wedding.create({
                "name": "Same Partner",
                "partner_1_id": self.partner_bride.id,
                "partner_2_id": self.partner_bride.id,
                "date": fields.Datetime.now() + timedelta(days=10),
            })

    def test_past_date_rejected(self):
        with self.assertRaises(ValidationError):
            self.Wedding.create({
                "name": "Past Wedding",
                "partner_1_id": self.partner_bride.id,
                "partner_2_id": self.partner_groom.id,
                "date": fields.Datetime.now() - timedelta(days=10),
            })

    def test_guest_summary_compute(self):
        self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Confirmed Guest",
            "attendance_state": "confirmed",
            "allowed_companions": 1,
            "confirmed_companions": 1,
        })
        self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Pending Guest",
            "attendance_state": "pending",
        })
        self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Declined Guest",
            "attendance_state": "declined",
        })
        # Confirmed guest brings 1 + 1 companion = 2 attendees
        self.assertEqual(self.wedding.confirmed_guests, 2)
        self.assertEqual(self.wedding.pending_guests, 1)
        self.assertEqual(self.wedding.guest_count, 3)

    def test_budget_summary_compute(self):
        self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": self.category.id,
            "description": "Line 1",
            "estimated_amount": 5000.0,
            "actual_amount": 4000.0,
        })
        self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": self.category.id,
            "description": "Line 2",
            "estimated_amount": 3000.0,
            "actual_amount": 2000.0,
        })
        self.assertEqual(self.wedding.estimated_budget, 8000.0)
        self.assertEqual(self.wedding.actual_spend, 6000.0)
        # target 10000 - spend 6000
        self.assertEqual(self.wedding.budget_diff, 4000.0)
        self.assertEqual(self.wedding.budget_usage_pct, 60.0)

    def test_budget_usage_zero_target(self):
        wedding = self.Wedding.create({
            "name": "No Target",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=10),
            "target_budget": 0.0,
        })
        self.BudgetLine.create({
            "wedding_id": wedding.id,
            "category_id": self.category.id,
            "description": "Spend only",
            "estimated_amount": 100.0,
            "actual_amount": 100.0,
        })
        self.assertEqual(wedding.budget_usage_pct, 0.0)

    def test_pending_tasks_compute(self):
        self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "Open task",
            "state": "pending",
        })
        self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "Done task",
            "state": "done",
        })
        self.assertEqual(self.wedding.pending_tasks, 1)
        self.assertEqual(self.wedding.task_count, 2)
