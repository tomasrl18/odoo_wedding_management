# -*- coding: utf-8 -*-
"""Tests for wedding.table: capacity, same-wedding and declined-guest constraints."""
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_wedding_table", "all", "wedding_management")
class TestWeddingTable(TestWeddingSetup):

    def _confirmed_guest(self, name, companions=0):
        return self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": name,
            "attendance_state": "confirmed",
            "allowed_companions": companions,
            "confirmed_companions": companions,
        })

    def test_occupancy_and_free_seats(self):
        table = self.Table.create({
            "wedding_id": self.wedding.id,
            "name": "Table 1",
            "capacity": 4,
        })
        g1 = self._confirmed_guest("G1", companions=1)  # 2 attendees
        g2 = self._confirmed_guest("G2")                # 1 attendee
        table.write({"guest_ids": [(4, g1.id), (4, g2.id)]})
        self.assertEqual(table.occupancy, 3)
        self.assertEqual(table.free_seats, 1)

    def test_over_capacity_rejected(self):
        table = self.Table.create({
            "wedding_id": self.wedding.id,
            "name": "Small Table",
            "capacity": 2,
        })
        g1 = self._confirmed_guest("G1", companions=1)  # 2 attendees
        g2 = self._confirmed_guest("G2")                # 1 attendee
        with self.assertRaises(ValidationError):
            table.write({"guest_ids": [(4, g1.id), (4, g2.id)]})

    def test_zero_capacity_rejected(self):
        with self.assertRaises(ValidationError):
            self.Table.create({
                "wedding_id": self.wedding.id,
                "name": "Zero Table",
                "capacity": 0,
            })

    def test_guest_from_other_wedding_rejected(self):
        other_wedding = self.Wedding.create({
            "name": "Other Wedding",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": self.wedding.date,
        })
        other_guest = self.Guest.create({
            "wedding_id": other_wedding.id,
            "name": "Other Guest",
            "attendance_state": "confirmed",
        })
        table = self.Table.create({
            "wedding_id": self.wedding.id,
            "name": "Table X",
            "capacity": 4,
        })
        with self.assertRaises(ValidationError):
            table.write({"guest_ids": [(4, other_guest.id)]})

    def test_declined_guest_rejected(self):
        declined = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Declined Guest",
            "attendance_state": "declined",
        })
        table = self.Table.create({
            "wedding_id": self.wedding.id,
            "name": "Table Y",
            "capacity": 4,
        })
        with self.assertRaises(ValidationError):
            table.write({"guest_ids": [(4, declined.id)]})

    def test_pending_guest_allowed_but_not_counted(self):
        pending = self.Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Pending Guest",
            "attendance_state": "pending",
        })
        table = self.Table.create({
            "wedding_id": self.wedding.id,
            "name": "Table Z",
            "capacity": 4,
        })
        table.write({"guest_ids": [(4, pending.id)]})
        # Pending guest has 0 actual attendees
        self.assertEqual(table.occupancy, 0)
