{
    "name": "Wedding Management",
    "summary": """
        Comprehensive wedding management for wedding planning companies:
        weddings, guests, tables, vendors, budgets, tasks, and timelines.
        """,
    "author": "Tomás Raigal",
    "maintainer": "Tomás Raigal",
    "license": "LGPL-3",
    "category": "Services",
    "version": "15.0.1.0.0",
    "currency": "EUR",
    "depends": [
        "base",
        "mail",
        "contacts",
    ],
    "data": [
        "security/wedding_security.xml",
        "security/ir.model.access.csv",
        "data/wedding_budget_category_data.xml",
        "data/wedding_timeline_type_data.xml",
        "views/wedding_guest_views.xml",
        "views/wedding_table_views.xml",
        "views/wedding_vendor_booking_views.xml",
        "views/wedding_budget_views.xml",
        "views/wedding_task_views.xml",
        "views/wedding_timeline_views.xml",
        "report/report_templates.xml",
        "views/wedding_event_views.xml",
        "views/wedding_menus.xml",
    ],
    "demo": [
        "demo/wedding_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 99.99,
    "images": [
        "static/description/banner.png",
    ],
    "assets": {
        "web.report_assets_common": [
            "wedding_management/static/src/css/wedding_report.css",
        ],
    },
}
