// Copyright (c) 2016, BS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trial Balance"] = {
	"filters": [
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Accounts",
			"get_query": function () {
				return {
					"doctype": "Accounts",
					"filters": {
						'is_group': false
					}
				}
			}
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
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
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
	],
}