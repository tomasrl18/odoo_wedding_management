Wedding Management for Odoo 15
=============================

Overview
--------
This module helps wedding planners manage weddings from the Odoo backend. It brings guests, seating, vendors, budgets, preparation tasks, and wedding-day schedules together in one application.

Features
--------
- Wedding planning: Manage couple contacts, dates, venues, responsible users, and attendance and budget summaries.
- Guest management: Track invitations, attendance, companions, menu preferences, and table assignments.
- Seating: Organize tables and review their capacity, occupancy, and available seats.
- Vendor bookings: Record services, agreed amounts, advance payments, balances, and payment deadlines.
- Budgets: Track estimated and actual expenses by category and record payment statuses.
- Tasks and timeline: Assign preparation tasks and organize wedding-day activities.
- Collaboration: Use chatter and activities on weddings, tasks, and vendor bookings.
- Reports: Print wedding summaries, guest and table lists, and budgets by category.
- Access control: Assign Wedding Coordinator and Wedding Manager roles, with company-based access to operational records.

Installation
------------
1. Copy the `wedding_management` addon folder into your Odoo custom addons directory, keeping its folder name unchanged.
2. Ensure that the parent custom addons directory is included in your Odoo configuration's `addons_path`.
3. Restart Odoo, enable developer mode, and update the Apps list.
4. Search for **Wedding Management** and install the module.
5. Assign the **Wedding Coordinator** or **Wedding Manager** role to the internal users who need access.

The module depends on `base`, `mail`, and `contacts`. Optional sample wedding data is available when demo data is enabled during installation.

Usage
-----
1. Open **Weddings > All Weddings** and create a wedding with a future date and two distinct couple contacts. Add its venue, responsible user, expected attendance, and target budget.
2. Add guests and record their invitation status, attendance, companions, and menu preferences.
3. Create tables and assign guests. Occupancy includes confirmed guests and their confirmed companions.
4. Add vendor bookings, agreed amounts, advances, and payment deadlines.
5. Enter estimated and actual expenses under **Budgets**. Budget lines are maintained separately from vendor bookings.
6. Create preparation tasks and arrange activities under **Timeline**.
7. Use **Print Summary**, **Print Guests & Tables**, or **Print Budget** from the wedding form.

Wedding Managers can maintain budget categories and timeline event types under **Weddings > Configuration**. Amounts use the wedding company's currency.

Invitation and payment statuses are tracked manually. The module does not provide a public RSVP form, automatic invitation delivery, or payment processing.

Compatibility
-------------
- Targets Odoo 15.0; module version: `15.0.1.0.0`.
- Requires an existing Odoo installation with PostgreSQL and the standard dependencies listed above.
- PDF reports require a working Odoo PDF rendering setup.
- Installation and runtime compatibility have not been verified as part of this documentation update.

Credits
-------
- Developer and maintainer: Tomás Raigal.

License
-------
The module manifest declares GNU LGPL v3.0 (`LGPL-3`). The bundled `LICENSE` file currently contains GNU GPL v3.0 text; these declarations are inconsistent and need to be reconciled by the maintainer.
