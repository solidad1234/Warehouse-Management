# Copyright (c) 2025, solidad kimeu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, now, today

class CustomStockEntry(Document):
    def on_submit(self):
        for row in self.items:
            if self.stock_entry_type == "Receipt":
                self.create_ledger_entry(
                    item=row.item_code,
                    warehouse=row.target_warehouse,
                    qty=row.qty,
                    rate=row.rate,
                    is_incoming=True
                )

            elif self.stock_entry_type == "Consume":
                self.create_ledger_entry(
                    item=row.item_code,
                    warehouse=row.source_warehouse,
                    qty=row.qty,
                    rate=self.get_current_valuation_rate(row.item_code, row.source_warehouse),
                    is_incoming=False
                )

            elif self.stock_entry_type == "Transfer":
                valuation_rate = self.get_current_valuation_rate(row.item_code, row.source_warehouse)
                # from source
                self.create_ledger_entry(
                    item=row.item_code,
                    warehouse=row.source_warehouse,
                    qty=row.qty,
                    rate=valuation_rate,
                    is_incoming=False
                )
                #  to target
                self.create_ledger_entry(
                    item=row.item_code,
                    warehouse=row.target_warehouse,
                    qty=row.qty,
                    rate=valuation_rate,
                    is_incoming=True
                )

    def get_current_valuation_rate(self, item, warehouse):
        result = frappe.db.sql("""
            SELECT qty_after_transaction, valuation_rate
            FROM `tabCustom Stock Ledger Entry`
            WHERE item_code=%s AND warehouse=%s
            ORDER BY posting_datetime DESC
            LIMIT 1
        """, (item, warehouse), as_dict=True)

        return result[0].valuation_rate if result else 0

    def create_ledger_entry(self, item, warehouse, qty, rate, is_incoming):
        current_balance = frappe.db.sql("""
            SELECT qty_after_transaction, valuation_rate
            FROM `tabCustom Stock Ledger Entry`
            WHERE item_code=%s AND warehouse=%s
            ORDER BY posting_datetime DESC
            LIMIT 1
        """, (item, warehouse), as_dict=True)

        prev_qty = current_balance[0].qty_after_transaction if current_balance else 0
        prev_rate = current_balance[0].valuation_rate if current_balance else 0

        if is_incoming:
            new_qty = prev_qty + qty
            new_rate = (prev_qty * prev_rate + qty * rate) / new_qty if new_qty else rate
        else:
            new_qty = prev_qty - qty
            new_rate = prev_rate

        ledger_entry = frappe.get_doc({
            "doctype": "Custom Stock Ledger Entry",
            "item_code": item,
            "warehouse": warehouse,
            "posting_datetime": now_datetime(),
            "actual_qty": qty if is_incoming else -qty,
            "valuation_rate": new_rate,
            "qty_after_transaction": new_qty,
            "stock_value": new_qty * new_rate,
            "posting_date": today(),
            "posting_time": now(),
            "voucher_type": "Custom Stock Entry",
            "voucher_no": self.name
        })
        ledger_entry.insert(ignore_permissions=True)
        ledger_entry.submit()

