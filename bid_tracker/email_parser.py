import frappe
import re 
from frappe.utils import strip_html


def process_incoming_email(doc, method=None):
    # 1. Accept 'Email' (for production) and 'Other' (for our local test)
    if doc.communication_medium not in ["Email", "Other"] or doc.sent_or_received != "Received":
        return
        
    subject = str(doc.subject or "")
    content = str(doc.text_content or strip_html(doc.content or ""))
    full_text = subject + " " + content

    # 2. Look for pricing/schedule keywords
    if "pricing" not in subject.lower() and "schedule" not in subject.lower():
        return

    # 3. Regex to find the RFP ID
    rfp_match = re.search(r'([A-Z0-9]+-[A-Z0-9]+-RFP-\d{4}-\d+)', full_text, re.IGNORECASE)
    if not rfp_match:
        return
        
    rfp_id = rfp_match.group(1)

    # 4. Find the matching Bid Record
    bids = frappe.db.sql("""
        SELECT name FROM `tabBid Record`
        WHERE bid_title LIKE %s
    """, (f"%{rfp_id}%",), as_dict=True)
    
    if not bids:
        frappe.logger().warning(f"Email Parser: Found RFP {rfp_id} but no matching Bid Record exists.")
        return
        
    bid_name = bids[0].name

    # 5. Extract the Total Cost
    total_match = re.search(r'total.*?\$([0-9,]+\.\d{2})', content, re.IGNORECASE)
    
    if total_match:
        clean_amount = total_match.group(1).replace(',', '')
        amount = float(clean_amount)
        
        if amount > 0:
            bid_doc = frappe.get_doc("Bid Record", bid_name)
            
            # 6. IDEMPOTENCY CHECK: Does a quote from this sender already exist for this bid?
            existing_entries = frappe.get_all(
                "Bid Cost Entry",
                filters={
                    "bid_record": bid_name,
                    "description": ["like", f"%{doc.sender}%"]
                },
                fields=["name", "amount"]
            )
            
            if existing_entries:
                existing_entry = existing_entries[0]
                
                # Scenario A: Exact duplicate email
                if float(existing_entry.amount) == amount:
                    frappe.logger().info(f"Ignored duplicate pricing email from {doc.sender} for {bid_name}.")
                    return
                
                # Scenario B: Subcontractor revised their quote
                else:
                    frappe.db.set_value("Bid Cost Entry", existing_entry.name, "amount", amount)
                    frappe.db.set_value("Bid Cost Entry", existing_entry.name, "description", f"Automated material pricing (UPDATED) from {doc.sender}. Subject: {subject}")
                    
                    bid_doc.add_comment("Info", f"🔄 Subcontractor ({doc.sender}) updated their quote from **${existing_entry.amount:,.2f}** to **${amount:,.2f}**.")
                    frappe.db.commit()
                    return

            # Scenario C: Brand new quote (Original Logic)
            cost_entry = frappe.get_doc({
                "doctype": "Bid Cost Entry",
                "bid_record": bid_name,
                "cost_type": "Materials",
                "description": f"Automated material pricing from {doc.sender}. Subject: {subject}",
                "amount": amount,
                "added_by": frappe.session.user
            })
            cost_entry.insert(ignore_permissions=True)
            
            bid_doc.add_comment("Info", f"💰 Automatically logged Material Cost of **${amount:,.2f}** from subcontractor email.")
            frappe.db.commit()