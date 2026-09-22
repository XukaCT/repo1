frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {
        // Only show if the record is saved and the status is Open
        if (!frm.is_new() && frm.doc.status === "Open") {
            
            // Wait 500ms to let standard ERPNext build the "Create" menu first
            setTimeout(() => {
                frm.add_custom_button(__('Bid Record'), function() {
                    frappe.call({
                        method: 'bid_tracker.bid_management.api.create_bid_from_opportunity',
                        args: { opportunity_name: frm.doc.name },
                        callback: function(r) {
                            if (!r.exc && r.message) {
                                frappe.show_alert({message: __('Bid Record Created'), indicator: 'green'});
                                frappe.set_route("Form", "Bid Record", r.message);
                            }
                        }
                    });
                }, __('Create'));
            }, 500);
            
        }
    }
});
