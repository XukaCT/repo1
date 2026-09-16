frappe.ui.form.on("Bid Record", {
  refresh(frm) {
    initialize_financial_fields(frm);

    if (!frm.is_new() && !frm.doc.opportunity) {
        frm.add_custom_button(__('Create Opportunity'), function() {
            frappe.call({
                method: 'warroom_app.api.create_opportunity_from_bid', 
                args: {
                    bid_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.status === 'success') {
                        frappe.show_alert({
                            message: __('Opportunity created and linked successfully: ' + r.message.new_opportunity_id),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(r.message.message || __('Failed to create opportunity.'));
                    }
                }
            });
        }, __('Actions'));
    }
  },

  estimated_contract_value(frm) {
    calculate_metrics(frm);
  },
});

function initialize_financial_fields(frm) {
  frm.set_value("total_timesheet_cost", frm.doc.total_timesheet_cost || 0);
  frm.set_value("total_manual_cost", frm.doc.total_manual_cost || 0);
  frm.set_value("total_bid_cost", frm.doc.total_bid_cost || 0);
  frm.set_value("estimated_profit", frm.doc.estimated_profit || 0);
  frm.set_value("roi_ratio", frm.doc.roi_ratio || 0);
}

function calculate_metrics(frm) {
  let contract = frm.doc.estimated_contract_value || 0;
  let total_cost = frm.doc.total_bid_cost || 0;
  let profit = contract - total_cost;
  
  frm.set_value("estimated_profit", profit);
  
  if (total_cost > 0) {
    frm.set_value("roi_ratio", (profit / total_cost) * 100);
  } else {
    frm.set_value("roi_ratio", 0);
  }
}