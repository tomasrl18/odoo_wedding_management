# -*- coding: utf-8 -*-
"""Tests for wedding.vendor.booking: amount constraints and balance computation."""
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_wedding_vendor", "all", "wedding_management")
class TestWeddingVendor(TestWeddingSetup):

    def test_balance_due_compute(self):
        booking = self.Vendor.create({
            "wedding_id": self.wedding.id,
            "partner_id": self.partner_vendor.id,
            "service_type": "catering",
            "amount_agreed": 5000.0,
            "advance_paid": 2000.0,
        })
        self.assertEqual(booking.balance_due, 3000.0)

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValidationError):
            self.Vendor.create({
                "wedding_id": self.wedding.id,
                "partner_id": self.partner_vendor.id,
                "amount_agreed": -100.0,
            })

    def test_negative_advance_rejected(self):
        with self.assertRaises(ValidationError):
            self.Vendor.create({
                "wedding_id": self.wedding.id,
                "partner_id": self.partner_vendor.id,
                "amount_agreed": 1000.0,
                "advance_paid": -50.0,
            })

    def test_advance_exceeding_agreed_rejected(self):
        with self.assertRaises(ValidationError):
            self.Vendor.create({
                "wedding_id": self.wedding.id,
                "partner_id": self.partner_vendor.id,
                "amount_agreed": 1000.0,
                "advance_paid": 1500.0,
            })

    def test_advance_equal_agreed_ok(self):
        booking = self.Vendor.create({
            "wedding_id": self.wedding.id,
            "partner_id": self.partner_vendor.id,
            "amount_agreed": 1000.0,
            "advance_paid": 1000.0,
        })
        self.assertEqual(booking.balance_due, 0.0)

    def test_total_cost_on_wedding(self):
        self.Vendor.create({
            "wedding_id": self.wedding.id,
            "partner_id": self.partner_vendor.id,
            "amount_agreed": 3000.0,
        })
        self.Vendor.create({
            "wedding_id": self.wedding.id,
            "partner_id": self.partner_vendor.id,
            "amount_agreed": 2000.0,
        })
        self.assertEqual(self.wedding.vendor_count, 2)
