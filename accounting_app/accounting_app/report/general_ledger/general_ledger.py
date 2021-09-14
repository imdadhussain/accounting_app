# Copyright (c) 2013, BS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from frappe.utils import getdate, cstr, flt

def execute(filters=None):
    columns, data = [], []
    validate_filters(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def validate_filters(filters):
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date must be before To Date"))


def get_columns(filters):
    columns = [
        {
            "label": _("GL Entry"),
            "fieldname": "gl_entry",
            "fieldtype": "Link",
            "options": "GL Entry",
            #"hidden": 1
        },
		{
            "label": _("Posting Timestamp"),
            "fieldname": "posting_datetime",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Accounts"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Accounts",
            "width": 180
        },
        {
            "label": _("Debit (INR)"),
            "fieldname": "debit_amount",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Credit (INR)"),
            "fieldname": "credit_amount",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Balance (INR)"),
            "fieldname": "balance",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 120
        },
        {
            "label": _("Reference Doc"),
            "fieldname": "reference_doc",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 150
        },
        {
            "label": _("Reason"),
            "fieldname": "reason",
            "width": 250
        }
    ]
    return columns

def get_data(filters):
    gl_entries = get_gl_entries(filters)
    data = get_data_with_opening_closing(filters, gl_entries)
    result = get_result_as_list(data, filters)
    return result

def get_gl_entries(filters):
    order_by_statement = "order by reference_doc, account"

    gl_entries = frappe.db.sql(
        """
        select name as gl_entry, posting_datetime, account, voucher_type, reference_doc, debit, credit, reason
        from `tabGL Entry` {conditions} {order_by_statement}
        """.format(conditions=get_conditions(filters),order_by_statement=order_by_statement),
        filters, as_dict=1)

    return gl_entries

def get_conditions(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    voucher_type = filters.get('voucher_type')
    reference_doc = filters.get("reference_doc")
    account = filters.get("account")

    conditions = []
    if account:
        lft, rgt = frappe.db.get_value("Accounts", filters["account"], ["lft", "rgt"])
        conditions.append("""account in (select name from tabAccounts
            where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))
    if voucher_type:
        conditions.append("voucher_type=%(voucher_type)s")

    if reference_doc:
        conditions.append("reference_doc=%(reference_doc)s")

    conditions.append("transaction_date>=%(from_date)s")
    conditions.append("transaction_date<=%(to_date)s")
    
    from frappe.desk.reportview import build_match_conditions
    match_conditions = build_match_conditions("GL Entry")

    if match_conditions:
        conditions.append(match_conditions)
    
    return "where {}".format(" and ".join(conditions)) if conditions else ""

def get_totals_dict():
    def _get_debit_credit_dict(label):
        return _dict(
            account="'{0}'".format(label),
            debit_amount=0.0,
            credit_amount=0.0
        )
    return _dict(
        opening = _get_debit_credit_dict(_('Opening')),
        total = _get_debit_credit_dict(_('Total')),
        closing = _get_debit_credit_dict(_('Closing (Opening + Total)')))

def get_data_with_opening_closing(filters, gl_entries):
    data = []

    totals, entries = get_accountwise_gle(filters, gl_entries)
    data.append(totals.opening)
    data += entries
    data.append(totals.total)
    data.append(totals.closing)

    return data


def get_accountwise_gle(filters, gl_entries):
    totals = get_totals_dict()
    entries = []

    def update_value_in_dict(data, key, gle):
        data[key].debit_amount += flt(gle.debit)
        data[key].credit_amount += flt(gle.credit)

    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
    for gle in gl_entries:
        print(gle,"GLE")
        if gle.posting_datetime.date() < from_date:
            update_value_in_dict(totals, 'opening', gle)
            update_value_in_dict(totals, 'closing', gle)

        elif gle.posting_datetime.date() <= to_date:
            update_value_in_dict(totals, 'total', gle)
            update_value_in_dict(totals, 'closing', gle)

        entries.append(gle)

    return totals, entries

    
def get_result_as_list(data, filters):
    balance = 0
    print(data)
    for d in data:
        print(d)
        if not d.get('posting_date'):
            balance = 0
        balance = get_balance(d, balance, 'debit_amount', 'credit_amount')
        d['balance'] = balance

    return data

def get_balance(row, balance, debit_field, credit_field):
    balance += (row.get(debit_field, 0) -  row.get(credit_field, 0))
    return balance


