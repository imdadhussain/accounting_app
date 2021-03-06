// Copyright (c) 2016, BS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["General Ledger"] = {
	"filters": [
		{
            "label": __("Fiscal Year"),
            "fieldname": "fiscal_year",
			"fieldtype": "Link",
			"options": "Fiscal Year",
			on_change: function(){
				let fiscal_year = frappe.query_report.get_filter_value('fiscal_year');
				frappe.db.get_value('Fiscal Year', fiscal_year, ['start_date', 'end_date']).then(
					response => {
						let values = response.message;
						frappe.query_report.set_filter_value('from_date', values.start_date);
						frappe.query_report.set_filter_value('to_date', values.end_date);
					});
			}
        },
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": [
				'',
				__("Purchase Invoice"),
				__("Sale Invoice"),
				__("Journal Entry"),
				__("Payment Entry")
			]
		},
		{
			"fieldname": "reference_doc",
			"label": "Reference Document",
			"fieldtype": "Data"
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Accounts"
		}
	]
};