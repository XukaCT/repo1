import frappe

@frappe.whitelist()
def recalculate_bid(bid_name: str):
    doc = frappe.get_doc("Bid Record", bid_name)
    doc.calculate_totals()
    doc.save(ignore_permissions=True)
    return {
        "name": doc.name,
        "total_manual_cost": doc.total_manual_cost,
        "total_timesheet_cost": doc.total_timesheet_cost,
        "total_bid_cost": doc.total_bid_cost,
        "estimated_profit": doc.estimated_profit,
        "roi_ratio": doc.roi_ratio,
    }

def update_bid_record_totals(doc, method=None):
    if not doc.bid_record:
        return
    bid = frappe.get_doc("Bid Record", doc.bid_record)
    bid.calculate_totals()
    bid.db_set("total_manual_cost", bid.total_manual_cost)
    bid.db_set("total_timesheet_cost", bid.total_timesheet_cost)
    bid.db_set("total_bid_cost", bid.total_bid_cost)
    bid.db_set("estimated_profit", bid.estimated_profit)
    bid.db_set("roi_ratio", bid.roi_ratio)

@frappe.whitelist()
def create_bid_from_opportunity(opportunity_name):
    opp = frappe.get_doc("Opportunity", opportunity_name)
    
    # (The Bid Assessment Gatekeeper has been temporarily removed so you can test)

    # 1. Idempotency check: Ensure a Bid Record doesn't already exist for this Opportunity
    if frappe.db.exists("Bid Record", {"opportunity": opportunity_name}):
        frappe.throw("A Bid Record already exists for this Opportunity.")
        
    # 2. Translate War Room sector keys to allowed Bid Record sector options
    raw_sector = opp.get("custom_sector") or "other"
    sector_map = {
        "it_services": "IT",
        "healthcare": "Healthcare",
        "construction": "Construction",
        "cleaning": "Other",
        "facility_management": "Other",
        "transportation": "Other",
        "other": "Other"
    }
    mapped_sector = sector_map.get(raw_sector.lower(), "Other")

    # 3. Create the Bid Record
    bid = frappe.get_doc({
        "doctype": "Bid Record",
        "bid_title": opp.title or opp.customer_name or opp.party_name,
        "opportunity": opp.name,
        "customer": opp.party_name if opp.opportunity_from == "Customer" else "",
        "sector": mapped_sector,
        "estimated_contract_value": opp.get("custom_estimated_value") or opp.opportunity_amount,
        "bid_submission_date": opp.get("custom_close_date"),
        "war_room_reference": opp.get("custom_war_room_reference"),
        "bid_owner": frappe.session.user
    })
    
    bid.insert(ignore_permissions=True)
    return bid.name