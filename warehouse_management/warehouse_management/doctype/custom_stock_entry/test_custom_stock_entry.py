# Copyright (c) 2025, solidad kimeu and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate
import random

class TestCustomStockEntry(FrappeTestCase):
    def setUp(self):
        self.item_code = f"TEST-ITEM-{random.randint(1000, 9999)}"

        # test item
        if not frappe.db.exists("Custom Item", self.item_code):
            frappe.get_doc({
                "doctype": "Custom Item",
                "item_code": self.item_code,
                "item_name": "Test Item",
                "uom": "Nos"
            }).insert(ignore_permissions=True)

        #  source warehouse 
        source_name = f"Test Source {random.randint(1000, 9999)}"
        source_doc = frappe.get_doc({
            "doctype": "Custom Warehouse",
            "warehouse_name": source_name
        }).insert(ignore_permissions=True)
        self.source_warehouse = source_doc.name

        #  target warehouse
        target_name = f"Test Target {random.randint(1000, 9999)}"
        target_doc = frappe.get_doc({
            "doctype": "Custom Warehouse",
            "warehouse_name": target_name
        }).insert(ignore_permissions=True)
        self.target_warehouse = target_doc.name

    def tearDown(self):
        frappe.db.delete("Custom Stock Entry", {"docstatus": ["<", 2]})
        frappe.db.delete("Custom Item", {"item_code": self.item_code})
        frappe.db.delete("Custom Warehouse", {"name": ["in", [self.source_warehouse, self.target_warehouse]]})

    def make_custom_stock_entry(self, entry_type):
        return frappe.get_doc({
            "doctype": "Custom Stock Entry",
            "stock_entry_type": entry_type,
            "posting_date": nowdate(),
            "source_warehouse": self.source_warehouse if entry_type in ["Consume", "Transfer"] else "",
            "target_warehouse": self.target_warehouse if entry_type in ["Receipt", "Transfer"] else "",
            "items": [
                {
                    "item_code": self.item_code,
                    "qty": 5,
                    "rate": 100,
                    "uom": "Nos",
                    "source_warehouse": self.source_warehouse if entry_type in ["Consume", "Transfer"] else "",
                    "target_warehouse": self.target_warehouse if entry_type in ["Receipt", "Transfer"] else "",
                }
            ]
        })

    def test_receipt_entry(self):
        doc = self.make_custom_stock_entry("Receipt")
        doc.insert()
        doc.submit()
        self.assertEqual(doc.docstatus, 1)

    def test_consume_entry(self):
        doc = self.make_custom_stock_entry("Consume")
        doc.insert()
        doc.submit()
        self.assertEqual(doc.docstatus, 1)

    def test_transfer_entry(self):
        doc = self.make_custom_stock_entry("Transfer")
        doc.insert()
        doc.submit()
        self.assertEqual(doc.docstatus, 1)
