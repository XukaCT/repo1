app_name = "bid_tracker"
app_title = "Bid Tracker"
app_publisher = "OpenAI"
app_description = "Custom ERPNext module for pre-contract bid tracking"
app_email = "bidtrackererpnext@gmail.com"
app_license = "MIT"

after_install = "bid_tracker.install.after_install"

doctype_js = {
    "Bid Record": "public/js/bid_record.js",
}

doc_events = {
    "Timesheet": {
        "on_update": "bid_tracker.bid_management.api.update_bid_record_totals",
        "on_submit": "bid_tracker.bid_management.api.update_bid_record_totals",
        "on_cancel": "bid_tracker.bid_management.api.update_bid_record_totals",
    },
    "Bid Cost Entry": {
        "on_update": "bid_tracker.bid_management.api.update_bid_record_totals",
        "on_trash": "bid_tracker.bid_management.api.update_bid_record_totals",
    },
    "Bid Record": {
        "on_update": "bid_tracker.events.broadcast_bid_update"
    }
}

add_to_apps_screen = [
    {
        "name": "bid_tracker",
        "logo": "/assets/frappe/images/frappe-framework-logo.svg",
        "title": "Bid Tracker",
        "route": "/desk/bid-tracker",
    }
]

fixtures = [
    {"dt": "Workflow", "filters": [["name", "in", ["Bid Record Workflow"]]]},
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {"dt": "Notification", "filters": [["name", "in", ["Bid Submitted Notification", "Bid Won Notification", "Bid Closed Notification", "Bid Withdrawn Notification"]]]},
    {"dt": "Role", "filters": [["name", "in", ["BD Team", "BD Manager", "Finance Reviewer", "Executive Viewer"]]]},
    {"dt": "Dashboard", "filters": [["name", "in", ["Pre-contract P&L Dashboard"]]]},
    {"dt": "Dashboard Chart", "filters": [["name", "in", ["Bid Status Breakdown"]]]},
    {"dt": "Number Card", "filters": [["name", "in", ["Total Bid Cost", "Estimated Contract Value", "ROI Ratio", "Estimated Profit"]]]},
    {"dt": "Report", "filters": [["name", "in", ["Bid PnL Summary", "Bid Cost Entry", "Bid Record Report"]]]},
]