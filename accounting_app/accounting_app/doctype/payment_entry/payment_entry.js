frappe.ui.form.on('Payment Entry', {
	refresh: function (form) {
		form.add_custom_button(__("General Ledger"), function () {
			frappe.route_options = {
				"voucher_no": form.doc.name,
				"from_date": form.doc.posting_date,
				"to_date": form.doc.posting_date
			};
			frappe.set_route("query-report", "General Ledger");
		});
	},

	transaction_type: function (form) {
		form.trigger('filters');
	},

	filters: function (form) {
		if (form.doc.transaction_type === "Sale Invoice") {
			form.set_query("paid_from", () => { return { filters: { "is_group": 0, "account_type": "Receivable" } } });
			form.set_query("paid_to", () => { return { filters: { "is_group": 0, "root_type": "Asset" } } });
		} else if (form.doc.transaction_type === "Purchase Invoice") {
			form.set_query("paid_from", () => { return { filters: { "is_group": 0, "root_type": "Expense" } } });
			form.set_query("paid_to", () => { return { filters: { "is_group": 0, "account_type": "Payable" } } });
		}
	}
});