# -*- coding: utf-8 -*-
# Copyright (c) 2021, BS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate

class SaleInvoice(Document):
    def validate(self):
        items = self.get('items')
        for item in items:
            if int(item.qty) <= 0:
                frappe.throw(_("Item quantity cannot be negative. One or more quantity is required for each product"))
            if int(item.rate) <= 0:
                frappe.throw(_("Item rate must be non zero"))
            if int(item.amount) == 0:
                frappe.throw(_("Amount cannot be zero"))

    def on_submit(self):
        self.balance_change()
        fiscal_year = frappe.get_all('Fiscal Year', filters = {'start_date' : ['<=', nowdate()], 'end_date' : ['>=', nowdate()]})
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'transaction_date': nowdate(),
            'fiscal_year': fiscal_year[0].name,
            'voucher_type': self.doctype,
            'reference_doc': self.name,
            'against_account': self.assets_account,
            'account': self.debit_to,
            'debit': self.total_amount
        })
        doc.insert()

        # altering goods transaction: remove from asset account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'transaction_date': nowdate(),
            'fiscal_year': fiscal_year[0].name,
            'voucher_type': self.doctype,
            'reference_doc': self.name,
            'against_account': self.debit_to,
            'account': self.assets_account,
            'credit': self.total_amount
        })
        doc.insert()

    def balance_change(self):
        self.perform_balance_change(self.get("debit_to"), "debit")
        self.perform_balance_change(self.get("assets_account"), "income")

    def perform_balance_change(self, account, account_type):
        doc = frappe.get_doc("Accounts", account)
        if doc.account_balance:
            if account_type == "debit":
                doc.account_balance += int(self.get("total_amount"))
            elif account_type == "income":
                doc.account_balance -= int(self.get("total_amount"))
            doc.save()

    def on_cancel(self):
        # reverse transactions
        # altering goods transaction: insert to asset account
        fiscal_year = frappe.get_all('Fiscal Year', filters = {'start_date' : ['<=', nowdate()], 'end_date' : ['>=', nowdate()]})
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': now_datetime(),
            'transaction_date': nowdate(),
            'fiscal_year': fiscal_year[0].name,
            'voucher_type': self.doctype,
            'reference_doc': self.name,
            'against_account': self.debit_to,
            'account': self.assets_account,
            'debit': self.total_amount
        })
        doc.insert()

        #  remove money: debit account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': now_datetime(),
            'transaction_date': nowdate(),
            'fiscal_year': fiscal_year[0].name,
            'voucher_type': self.doctype,
            'reference_doc': self.name,
            'against_account': self.assets_account,
            'account': self.debit_to,
            'credit': self.total_amount
        })
        doc.insert()

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    doclist = get_mapped_doc("Sale Invoice", source_name , {
        "Sale Invoice": {
            "doctype": "Payment Entry",
            "field_map": {
                "name": "reference_invoice",
                "doctype": "transaction_type",
                "total_amount": "payment_amount",
                "debit_to": "paid_from",
                "assets_account": "paid_to"
            },
            "validation": {
                "docstatus": ["=", 1]
            }
        }
    }, target_doc)

    return doclist
