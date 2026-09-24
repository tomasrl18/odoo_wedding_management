# -*- coding: utf-8 -*-
"""Tests for wedding.budget.line: totals, usage and no double counting."""
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_wedding_budget", "all", "wedding_management")
class TestWeddingBudget(TestWeddingSetup):

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValidationError):
            self.BudgetLine.create({
                "wedding_id": self.wedding.id,
                "category_id": self.category.id,
                "estimated_amount": -10.0,
            })

    def test_negative_actual_rejected(self):
        with self.assertRaises(ValidationError):
            self.BudgetLine.create({
                "wedding_id": self.wedding.id,
                "category_id": self.category.id,
                "actual_amount": -10.0,
            })

    def test_totals_by_category(self):
        cat2 = self.BudgetCategory.create({"name": "Category 2"})
        self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": self.category.id,
            "estimated_amount": 1000.0,
            "actual_amount": 800.0,
        })
        self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": self.category.id,
            "estimated_amount": 500.0,
            "actual_amount": 400.0,
        })
        self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": cat2.id,
            "estimated_amount": 200.0,
            "actual_amount": 200.0,
        })
        self.assertEqual(self.wedding.estimated_budget, 1700.0)
        self.assertEqual(self.wedding.actual_spend, 1400.0)

    def test_vendor_amounts_not_double_counted(self):
        """Vendor agreed amounts must NOT be added to the wedding spend."""
        self.Vendor.create({
            "wedding_id": self.wedding.id,
            "partner_id": self.partner_vendor.id,
            "amount_agreed": 5000.0,
        })
        self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": self.category.id,
            "estimated_amount": 100.0,
            "actual_amount": 100.0,
        })
        # Spend comes only from budget lines, not vendor bookings
        self.assertEqual(self.wedding.actual_spend, 100.0)
        self.assertEqual(self.wedding.estimated_budget, 100.0)

    def test_payment_state_default(self):
        line = self.BudgetLine.create({
            "wedding_id": self.wedding.id,
            "category_id": self.category.id,
            "estimated_amount": 100.0,
        })
        self.assertEqual(line.payment_state, "unpaid")
