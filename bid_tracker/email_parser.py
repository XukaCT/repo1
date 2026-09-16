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

    # 4. Find the matching Bid Record (Title search only to avoid missing column error)
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
            # 6. Create the Bid Cost Entry!
            cost_entry = frappe.get_doc({
                "doctype": "Bid Cost Entry",
                "bid_record": bid_name,
                "cost_type": "Materials",
                "description": f"Automated material pricing from {doc.sender}. Subject: {subject}",
                "amount": amount,
                "added_by": frappe.session.user  # Forces Frappe to use your valid Admin account
            })
            cost_entry.insert(ignore_permissions=True)
            
            # Optional: Add an automatic comment on the Bid Record alerting the team
            bid_doc = frappe.get_doc("Bid Record", bid_name)
            bid_doc.add_comment("Info", f"🤖 Automatically logged Material Cost of **${amount:,.2f}** from subcontractor email.")
            
            frappe.db.commit()