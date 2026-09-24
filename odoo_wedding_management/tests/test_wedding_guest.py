# -*- coding: utf-8 -*-
"""Tests for wedding.guest: attendee computation and companion constraint."""
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_wedding_guest", "all", "wedding_management")
class TestWeddingGuest(TestWeddingSetup):

    def test_attendees_confirmed_with_companions(self):
        guest = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Guest A",
            "attendance_state": "confirmed",
            "allowed_companions": 2,
            "confirmed_companions": 2,
        })
        self.assertEqual(guest.actual_attendees, 3)

    def test_attendees_confirmed_no_companions(self):
        guest = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Guest B",
            "attendance_state": "confirmed",
        })
        self.assertEqual(guest.actual_attendees, 1)

    def test_attendees_pending_is_zero(self):
        guest = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Guest C",
            "attendance_state": "pending",
            "confirmed_companions": 1,
            "allowed_companions": 1,
        })
        # Companions only count when attendance is confirmed
        self.assertEqual(guest.actual_attendees, 0)

    def test_attendees_declined_is_zero(self):
        guest = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Guest D",
            "attendance_state": "declined",
            "confirmed_companions": 1,
            "allowed_companions": 1,
        })
        self.assertEqual(guest.actual_attendees, 0)

    def test_attendees_recompute_on_state_change(self):
        guest = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Guest E",
            "attendance_state": "pending",
            "allowed_companions": 1,
            "confirmed_companions": 1,
        })
        self.assertEqual(guest.actual_attendees, 0)
        guest.write({"attendance_state": "confirmed"})
        self.assertEqual(guest.actual_attendees, 2)

    def test_companions_exceeding_allowed_rejected(self):
        with self.assertRaises(ValidationError):
            self.Guest.create({
                "wedding_id": self.wedding.id,
                "name": "Guest F",
                "allowed_companions": 1,
                "confirmed_companions": 2,
            })

    def test_companions_equal_allowed_ok(self):
        guest = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Guest G",
            "allowed_companions": 2,
            "confirmed_companions": 2,
        })
        self.assertEqual(guest.confirmed_companions, 2)
