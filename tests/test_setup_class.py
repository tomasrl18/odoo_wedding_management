# -*- coding: utf-8 -*-
"""Shared fixtures for wedding_management tests.

Creates the minimal records every suite needs: two partners (the couple),
a wedding, a vendor partner, a budget category and a timeline type.
No test methods live here, so the loader imports it but adds no tests.
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "all", "wedding_management")
class TestWeddingSetup(TransactionCase):
    """Base class holding the common fixtures for all wedding tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Wedding = cls.env["wedding.event"]
        cls.Guest = cls.env["wedding.guest"]
        cls.Table = cls.env["wedding.table"]
        cls.Vendor = cls.env["wedding.vendor.booking"]
        cls.BudgetLine = cls.env["wedding.budget.line"]
        cls.BudgetCategory = cls.env["wedding.budget.category"]
        cls.Task = cls.env["wedding.task"]
        cls.TimelineEvent = cls.env["wedding.timeline.event"]
        cls.TimelineType = cls.env["wedding.timeline.type"]
        cls.Partner = cls.env["res.partner"]
        cls.Company = cls.env["res.company"]

        # Partners
        cls.partner_bride = cls.Partner.create({"name": "Test Bride"})
        cls.partner_groom = cls.Partner.create({"name": "Test Groom"})
        cls.partner_vendor = cls.Partner.create({"name": "Test Vendor"})

        # A wedding in the future
        cls.wedding = cls.Wedding.create({
            "name": "Test Wedding",
            "partner_1_id": cls.partner_bride.id,
            "partner_2_id": cls.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=30),
            "venue": "Test Venue",
            "target_budget": 10000.0,
            "expected_guests": 50,
            "state": "planning",
        })

        # Config records
        cls.category = cls.BudgetCategory.create({"name": "Test Category"})
        cls.timeline_type = cls.TimelineType.create({"name": "Test Event Type"})
