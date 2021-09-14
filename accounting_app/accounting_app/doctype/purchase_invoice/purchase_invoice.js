frappe.ui.form.on('Purchase Invoice', {
	setup: function(form){
		form.set_query("party", function(){
			return {
				filters: {
					"party_type": "Supplier"
				}
			}
		})
		form.set_query("expense_account", function(){
			return {
				filters: {
					"root_type": "Expense",
					"is_group": 0
				}
			}
		})
		form.set_query("credit_to", function(){
			return {
				filters: {
					"account_type": "Payable",
					"is_group": 0
				}
			}
		})
	},
	refresh: function (form) {
		form.add_custom_button(__("General Ledger"), function () {
			frappe.route_options = {
				"voucher_no": form.doc.voucher_type,
				"from_date": form.doc.posting_timestamp,
				"to_date": form.doc.posting_timestamp
			};
			frappe.set_route("query-report", "General Ledger");
		});
		form.add_custom_button(__("Payment Entry"), function () {
			frappe.model.open_mapped_doc({
				method: "accounting_app.accounting_app.doctype.purchase_invoice.purchase_invoice.make_payment_entry",
				frm: cur_frm
			})
		}, __("Create"));
		form.page.set_inner_btn_group_as_primary(__('Create'));
	}
});

frappe.ui.form.on('Purchase Invoice Item', {
	item: function (form, cdt, cdn) {
		var document = frappe.get_doc(cdt, cdn);
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Item",
				name: document.item
			},
			callback: function (data) {
				frappe.model.set_value(cdt, cdn, "rate", data.message.standard_rate);
				frappe.model.set_value(cdt, cdn, "qty", 1);
				frappe.model.set_value(cdt, cdn, "amount", data.message.standard_rate * 1);
				set_total_quantity_and_amount(form)
			}
		})
	},
	qty: function (form, cdt, cdn) {
		var document = frappe.get_doc(cdt, cdn);
		frappe.model.set_value(cdt, cdn, "amount", document.rate * document.qty);
		set_total_quantity_and_amount(form)
	}
});

var set_total_quantity_and_amount = function (form) {
	var total_quantity = 0.0, total_amount = 0.0;
	form.doc.items.forEach(function (item){
		total_quantity += item.qty
		total_amount += item.amount
	});
	frappe.model.set_value(form.doctype, form.docname, "total_quantity", total_quantity);
	frappe.model.set_value(form.doctype, form.docname, "total_amount", total_amount);
}

