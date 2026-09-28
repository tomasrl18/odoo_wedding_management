# Wedding Management for Odoo 15

An Odoo backend application for wedding planners to manage weddings, guests, seating, vendor bookings, budgets, tasks, and wedding-day schedules.

| Metadata | Value |
| --- | --- |
| Odoo version | 15.0 |
| Module version | 15.0.1.0.0 |
| Deployment technical name | `wedding_management` (see installation note below) |
| Source directory | [`odoo_wedding_management/`](odoo_wedding_management/) |
| Author and maintainer | Tomás Raigal |
| License declared in manifest | LGPL-3 |
| Dependencies | `base`, `mail`, `contacts` |

## Features

- **Weddings:** couple contacts, date and time, venue, responsible user, company, expected guests, target budget, and computed summaries. Includes kanban, list, calendar, and form views.
- **Guests:** contact details, optional linked contact, invitation and attendance statuses, allowed and confirmed companions, menu choice, notes, and table assignment.
- **Tables:** capacity, assigned guests, computed occupancy, and available seats.
- **Vendors:** supplier contact, service type, contract date, agreed amount, advance paid, remaining balance, payment due date, and booking status.
- **Budgets:** categorized estimated and actual amounts, optional vendor, and manually maintained payment status.
- **Tasks:** responsible user, due date, priority, status, and overdue indicator, with kanban and list views.
- **Timeline:** event type, start and end times, location, responsible user, and notes.
- **Collaboration:** chatter and activities on weddings, tasks, and vendor bookings; chatter on guests.
- **Reports:** three QWeb PDF reports available through wedding form buttons.

## Installation

Use an existing Odoo 15 installation with PostgreSQL and the standard dependencies above. This repository contains the addon, not a complete Odoo server or deployment environment. PDF output requires a working Odoo PDF rendering setup.

**Important: deploy the addon directory as `wedding_management`.** The checked-in directory is named `odoo_wedding_management`, but XML action references, report template names, the menu icon path, and test references use the `wedding_management` namespace. Installing the directory under its current name can fail when Odoo resolves those references.

1. Copy the contents of `odoo_wedding_management/` into a directory named `wedding_management` inside your custom addons directory.
2. Include that parent custom addons directory in your Odoo configuration's `addons_path`, retaining the standard Odoo addons paths.
3. Restart Odoo, enable developer mode, and update the Apps list.
4. Search for **Wedding Management** and install it.
5. In user access settings, assign **Wedding Coordinator** or **Wedding Manager** to the relevant internal users. The application menu is named **Weddings**.

Expected deployment layout:

```text
custom-addons/
└── wedding_management/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    └── ...
```

Alternatively, from an Odoo source installation, initialize the module with the following command. Replace the configuration and database values with your own; the configuration must include the custom addons path.

```sh
./odoo-bin -c /path/to/odoo.conf -d wedding_db -i wedding_management --stop-after-init
```

To update an existing installation after deploying changes:

```sh
./odoo-bin -c /path/to/odoo.conf -d wedding_db -u wedding_management --stop-after-init
```

The module includes optional [demo data](odoo_wedding_management/demo/wedding_demo.xml) for a sample wedding, contacts, guests, tables, vendor bookings, budget lines, tasks, and timeline entries. It is loaded when demo data is enabled during installation.

## Configuration and access

| Role | Permissions |
| --- | --- |
| Wedding Coordinator | Read, create, edit, and delete weddings and their operational records; read budget categories and timeline types. |
| Wedding Manager | All coordinator permissions, plus create, edit, and delete budget categories and timeline types. |

Managers configure reference data under **Weddings → Configuration**:

- **Budget Categories:** Catering, Wedding Attire, Flowers, Music, Photography, Decoration, Rental, and Other Expenses are supplied.
- **Timeline Event Types:** Ceremony, Cocktail, Banquet, Photographs, Dance, and Other are supplied.

Both reference models support ordering and archiving and require unique names. They are shared across companies. Record rules restrict weddings and operational records to the user's currently allowed companies; records are not restricted to the assigned responsible user.

Amounts use the wedding company's currency. The manifest's `currency: EUR` metadata does not force wedding records to use euros.

## Typical workflow

1. Open **Weddings → All Weddings** and create a wedding with its name, future date and time, and two distinct couple contacts. Set the venue, responsible user, target budget, and expected attendance as needed.
2. Add guests from the wedding's **Guests** tab or the standalone **Guests** menu. Record invitation status, attendance, companions, and menu requirements.
3. Create tables and assign guests. Pending guests may be assigned but do not contribute to occupancy until confirmed. Remove a table assignment before marking an assigned guest as declined.
4. Record vendor bookings, agreed amounts, advances, and payment deadlines under **Vendors**.
5. Enter estimated and actual costs under **Budget**. Vendor booking amounts do not automatically create or update budget lines, so enter costs here for them to appear in wedding budget totals.
6. Add preparation tasks and wedding-day timeline entries. Tasks support Low, Normal, High, and Urgent priorities.
7. Review the wedding summary and use **Print Summary**, **Print Guests & Tables**, or **Print Budget**.

The models define the following statuses. These are stored selection values, not an enforced sequence of approval steps; statusbar views display only a subset by default.

| Record | Statuses |
| --- | --- |
| Wedding | Draft, Planning, Confirmed, Celebrated, Cancelled |
| Invitation | Pending, Sent, Answered |
| Attendance | Pending, Confirmed, Declined |
| Vendor booking | Proposal, Pending Confirmation, Contracted, Completed, Cancelled |
| Task | Pending, In Progress, Blocked, Done |
| Budget payment | Unpaid, Partially Paid, Paid |

## Calculations and validation

| Metric | Calculation |
| --- | --- |
| Actual attendees per guest | `1 + confirmed_companions` when attendance is confirmed; otherwise `0` |
| Confirmed guests on a wedding | Sum of actual attendees, including companions |
| Pending guests | Number of guest records with pending attendance, excluding companions |
| Table occupancy | Sum of actual attendees assigned to that table |
| Free seats | `max(0, capacity - occupancy)` |
| Wedding table occupancy | Total occupied seats divided by total capacity × 100; `0` without capacity |
| Estimated budget / actual spend | Sum of estimated / actual amounts on budget lines only |
| Budget difference | Target budget minus actual spend |
| Budget usage | Actual spend divided by target budget × 100; `0` when the target is not positive |
| Vendor balance due | Agreed amount minus advance paid |
| Pending tasks | All tasks whose status is not Done, including blocked tasks |

Guest and vendor counters count records, rather than individual attendees or distinct supplier contacts.

The model constraints reject identical couple contacts, past wedding dates when the date is validated, confirmed companions exceeding the allowance, nonpositive table capacity, negative budget/vendor amounts, advances exceeding the agreed amount, and timeline end times before their start times. Equal timeline start and end times are allowed. Guest/table constraints check wedding consistency, declined attendance, and table capacity, subject to the coverage limits below.

## Reports

| Report | Contents |
| --- | --- |
| Wedding Summary | Couple, venue, date, responsible user, company, status, budget and attendance summaries, vendors, and tasks |
| Guests and Tables | Guest contact details, companion counts, attendance, menus, table assignments, capacity, occupancy, and free seats |
| Budget by Category | Budget lines grouped by category, category subtotals, grand totals, payment statuses, and difference from the target |

Templates and report actions are defined in [`report_templates.xml`](odoo_wedding_management/report/report_templates.xml).

## Technical structure

```text
odoo_wedding_management/
├── __manifest__.py       # Dependencies, metadata, and data load order
├── models/               # Nine ORM models and business constraints
├── views/                # Backend views, actions, and menus
├── security/             # Roles, access rights, and company record rules
├── data/                 # Default categories and timeline types
├── demo/                 # Optional example records
├── report/               # QWeb PDF templates and actions
├── i18n/                 # Translation template and Spanish catalog
├── static/description/   # Application icon
└── tests/                # Odoo transaction tests
```

`wedding.event` is the parent of `wedding.guest`, `wedding.table`, `wedding.vendor.booking`, `wedding.budget.line`, `wedding.task`, and `wedding.timeline.event`. Their wedding relations use cascading deletion. `wedding.budget.category` and `wedding.timeline.type` provide shared reference data. Couple and supplier records use standard `res.partner` contacts.

## Tests

The suite uses Odoo `TransactionCase` and is tagged `post_install`, `-at_install`, and `wedding_management`. It covers wedding validation and summaries, companion counts, seating, vendor balances, budget calculations, task and timeline rules, role permissions, and company isolation.

Run it using an Odoo 15 environment and a dedicated test database, with the addon deployed under the technical name described above:

```sh
./odoo-bin -c /path/to/odoo.conf -d wedding_test -i wedding_management --test-enable --test-tags wedding_management --stop-after-init
```

For an already initialized test database, replace `-i` with `-u`. Tests require Odoo and its database environment; they are not a standalone pytest suite.

## Current limitations

These observations come from source inspection; they are not a claim that installation or runtime testing has passed.

- **Addon naming:** the deployment name must match the hard-coded `wedding_management` references, as described above.
- **Overdue refresh:** `is_overdue` is stored and recomputed when a task's due date or status changes. No scheduled daily recomputation is provided, so the value can become stale as days pass.
- **Seating validation coverage:** table capacity checks are triggered by writes to table capacity or its guest relation. Guest-side changes to attendance or companion counts do not explicitly rerun that capacity constraint. Wedding-consistency constraints also do not cover every reassignment path. Review these paths before relying on strict seating enforcement.
- **Companion input:** the code checks confirmed companions against the allowance but does not explicitly reject negative companion counts.
- **Manual operations:** invitation states and payment states are tracking fields. The addon supplies no public RSVP form, automatic invitation delivery, payment processing, invoicing integration, or synchronization between vendor bookings and budget lines.
- **Translations:** the repository includes `i18n/wedding_management.es.po`; automatic loading of this nonstandard filename has not been verified.
- **Runtime validation:** installation, browser behavior, PDF rendering, and the transaction suite must be verified in an Odoo 15 environment.

## License

The [manifest](odoo_wedding_management/__manifest__.py) declares **LGPL-3**. Author and maintainer: **Tomás Raigal**.
