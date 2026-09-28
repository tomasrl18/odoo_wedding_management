# -*- coding: utf-8 -*-
"""Tests for wedding.task and wedding.timeline.event: states and time constraint."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_wedding_task", "all", "wedding_management")
class TestWeddingTask(TestWeddingSetup):

    def test_task_default_state(self):
        task = self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "New Task",
        })
        self.assertEqual(task.state, "pending")

    def test_task_state_transitions(self):
        task = self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "Task",
            "state": "pending",
        })
        task.write({"state": "in_progress"})
        self.assertEqual(task.state, "in_progress")
        task.write({"state": "done"})
        self.assertEqual(task.state, "done")

    def test_overdue_compute(self):
        task = self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "Overdue Task",
            "due_date": (fields.Date.today() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "state": "pending",
        })
        self.assertTrue(task.is_overdue)

    def test_done_task_not_overdue(self):
        task = self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "Done Task",
            "due_date": (fields.Date.today() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "state": "done",
        })
        self.assertFalse(task.is_overdue)

    def test_future_task_not_overdue(self):
        task = self.Task.create({
            "wedding_id": self.wedding.id,
            "name": "Future Task",
            "due_date": (fields.Date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "state": "pending",
        })
        self.assertFalse(task.is_overdue)


@tagged("post_install", "-at_install", "test_wedding_timeline", "all", "wedding_management")
class TestWeddingTimeline(TestWeddingSetup):

    def test_timeline_end_before_start_rejected(self):
        start = fields.Datetime.now() + timedelta(days=30)
        with self.assertRaises(ValidationError):
            self.TimelineEvent.create({
                "wedding_id": self.wedding.id,
                "type_id": self.timeline_type.id,
                "start_time": start,
                "end_time": start - timedelta(hours=1),
            })

    def test_timeline_end_equal_start_ok(self):
        start = fields.Datetime.now() + timedelta(days=30)
        event = self.TimelineEvent.create({
            "wedding_id": self.wedding.id,
            "type_id": self.timeline_type.id,
            "start_time": start,
            "end_time": start,
        })
        self.assertTrue(event.id)

    def test_timeline_end_after_start_ok(self):
        start = fields.Datetime.now() + timedelta(days=30)
        event = self.TimelineEvent.create({
            "wedding_id": self.wedding.id,
            "type_id": self.timeline_type.id,
            "start_time": start,
            "end_time": start + timedelta(hours=2),
        })
        self.assertTrue(event.id)
