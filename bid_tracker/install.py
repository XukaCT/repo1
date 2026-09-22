import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_timesheet_bid_field()
    create_employee_hourly_rate_field()
    create_lead_custom_fields()

def create_timesheet_bid_field():
    custom_fields = {
        "Timesheet": [
            {
                "fieldname": "bid_record",
                "label": "Bid Record",
                "fieldtype": "Link",
                "options": "Bid Record",
                "insert_after": "parent_project",
                "read_only": 0,
                "in_list_view": 1,
            }
        ]
    }
    create_custom_fields(custom_fields, update=True)

def create_employee_hourly_rate_field():
    custom_fields = {
        "Employee": [
            {
                "fieldname": "hourly_rate",
                "label": "Hourly Rate",
                "fieldtype": "Currency",
                "insert_after": "company",
                # FIX: Wrapping 50 in quotes to pass Frappe's string formatting regex
                "default": "50",
            }
        ]
    }
    create_custom_fields(custom_fields, update=True)

def create_lead_custom_fields():
    # Define the fields once
    war_room_fields = [
        {
            "fieldname": "custom_war_room_reference",
            "label": "War Room Reference",
            "fieldtype": "Link",
            "options": "War Room Tender",
            "read_only": 1
        },
        {
            "fieldname": "custom_estimated_value",
            "label": "Estimated Contract Value",
            "fieldtype": "Currency"
        },
        {
            "fieldname": "custom_sector",
            "label": "Sector",
            "fieldtype": "Data"
        },
        {
            "fieldname": "custom_state",
            "label": "State",
            "fieldtype": "Data"
        },
        {
            "fieldname": "custom_close_date",
            "label": "Tender Close Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "custom_source_url",
            "label": "Source URL",
            "fieldtype": "Data",
            "options": "URL"
        }
    ]

    # Apply them to BOTH Lead and Opportunity
    custom_fields = {
        "Lead": war_room_fields,
        "Opportunity": war_room_fields
    }
    create_custom_fields(custom_fields, update=True)