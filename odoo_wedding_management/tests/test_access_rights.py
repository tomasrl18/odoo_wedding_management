# -*- coding: utf-8 -*-
"""Tests for access rights: groups and multi-company record rules."""
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .test_setup_class import TestWeddingSetup


@tagged("post_install", "-at_install", "test_access_rights", "all", "wedding_management")
class TestAccessRights(TestWeddingSetup):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Users = cls.env["res.users"]
        cls.group_coordinator = cls.env.ref("wedding_management.group_wedding_coordinator")
        cls.group_manager = cls.env.ref("wedding_management.group_wedding_manager")

        # A second company to test multi-company isolation
        cls.company_2 = cls.Company.create({
            "name": "Second Company",
            # inc_trans_core adds account fields with company-specific defaults;
            # clear them so the new company passes the company-compatibility check.
            "carrier_account_to_pay_id": False,
        })

        # Coordinator user in the default company
        cls.coordinator = cls.Users.create({
            "name": "Coordinator User",
            "login": "wedding_coordinator_test",
            "company_id": cls.env.company.id,
            "company_ids": [(6, 0, [cls.env.company.id])],
            "groups_id": [(6, 0, [cls.group_coordinator.id])],
        })
        # Manager user in the default company
        cls.manager = cls.Users.create({
            "name": "Manager User",
            "login": "wedding_manager_test",
            "company_id": cls.env.company.id,
            "company_ids": [(6, 0, [cls.env.company.id])],
            "groups_id": [(6, 0, [cls.group_manager.id])],
        })

    def test_coordinator_can_create_wedding(self):
        Wedding = self.Wedding.with_user(self.coordinator)
        wedding = Wedding.create({
            "name": "Coordinator Wedding",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=10),
        })
        self.assertTrue(wedding.id)

    def test_coordinator_can_manage_guests(self):
        Guest = self.Guest.with_user(self.coordinator)
        guest = Guest.create({
            "wedding_id": self.wedding.id,
            "name": "Coordinator Guest",
        })
        self.assertTrue(guest.id)
        guest.with_user(self.coordinator).write({"attendance_state": "confirmed"})
        self.assertEqual(guest.attendance_state, "confirmed")

    def test_coordinator_cannot_create_category(self):
        # Categories are manager-only (coordinator has read only)
        Category = self.BudgetCategory.with_user(self.coordinator)
        with self.assertRaises(Exception):
            Category.create({"name": "Coordinator Category"})

    def test_manager_can_create_category(self):
        Category = self.BudgetCategory.with_user(self.manager)
        category = Category.create({"name": "Manager Category"})
        self.assertTrue(category.id)

    def test_manager_implies_coordinator(self):
        # Manager group implies coordinator, so manager can also create weddings
        Wedding = self.Wedding.with_user(self.manager)
        wedding = Wedding.create({
            "name": "Manager Wedding",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=10),
        })
        self.assertTrue(wedding.id)

    def test_multicompany_isolation(self):
        # A wedding in company_2 must not be visible to the coordinator (company 1 only)
        other_wedding = self.Wedding.sudo().create({
            "name": "Other Company Wedding",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=10),
            "company_id": self.company_2.id,
        })
        Wedding = self.Wedding.with_user(self.coordinator)
        visible = Wedding.search([])
        self.assertNotIn(other_wedding, visible)
        # But the coordinator's own wedding is visible
        self.assertIn(self.wedding, visible)

    def test_multicompany_guest_isolation(self):
        # Guests of a company_2 wedding are hidden from company_1 coordinator
        other_wedding = self.Wedding.sudo().create({
            "name": "Other Company Wedding 2",
            "partner_1_id": self.partner_bride.id,
            "partner_2_id": self.partner_groom.id,
            "date": fields.Datetime.now() + timedelta(days=10),
            "company_id": self.company_2.id,
        })
        other_guest = self.Guest.sudo().create({
            "wedding_id": other_wedding.id,
            "name": "Other Company Guest",
        })
        Guest = self.Guest.with_user(self.coordinator)
        visible = Guest.search([])
        self.assertNotIn(other_guest, visible)
