import frappe

def broadcast_bid_update(doc, method):
    # Only broadcast if this bid is linked to the War Room
    if getattr(doc, "war_room_reference", None):
        
        # FIXED: Look up the War Room Tender by its actual ID (name)
        linked_tenders = frappe.get_all(
            "War Room Tender",
            filters={"name": doc.war_room_reference}
        )
        
        if linked_tenders:
            frappe.publish_realtime(
                'bid_status_changed',
                {
                    "bid_id": doc.name,
                    "war_room_reference": doc.war_room_reference,
                    "new_status": doc.bid_status
                }
            )