import frappe

def broadcast_bid_update(doc, method):
    # Only broadcast if this bid is linked to the War Room
    if getattr(doc, "war_room_reference", None):
        
        linked_tenders = frappe.get_all(
            "War Room Tender",
            filters={"name": doc.war_room_reference}
        )
        
        if linked_tenders:
            # 1. Get the correct workflow status (workflow.json uses "status", not "bid_status")
            current_status = doc.get("status") or "Draft"
            
            # 2. Map the Bid Tracker workflow state to a War Room Tender state
            tender_status = "pursued" # Default for Draft, Qualifying, Active, Submitted
            
            if current_status == "Won":
                tender_status = "won"
            elif current_status in ["Lost", "Withdrawn"]:
                tender_status = current_status.lower()

            # 3. Update the War Room Tender in the database
            frappe.db.set_value("War Room Tender", doc.war_room_reference, "status", tender_status)
            
            # 4. Force commit so the frontend fetch sees the change immediately
            frappe.db.commit() 
            
            # 5. Broadcast the refresh event to the React frontend
            frappe.publish_realtime(
                'bid_status_changed',
                {
                    "bid_id": doc.name,
                    "war_room_reference": doc.war_room_reference,
                    "new_status": current_status
                }
            )

def map_lead_to_opportunity(doc, method):
    """Automatically copy War Room data when an Opportunity is created from a Lead"""
    if doc.opportunity_from == "Lead" and doc.party_name:
        lead = frappe.get_doc("Lead", doc.party_name)
        
        # If the Lead came from the War Room, copy the fields over
        if lead.get("custom_war_room_reference"):
            doc.custom_war_room_reference = lead.custom_war_room_reference
            doc.custom_estimated_value = lead.custom_estimated_value
            doc.custom_sector = lead.custom_sector
            doc.custom_state = lead.custom_state
            doc.custom_close_date = lead.custom_close_date
            doc.custom_source_url = lead.custom_source_url