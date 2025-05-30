import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate
from unittest.mock import patch

class TestSalesInvoiceSubmit(FrappeTestCase):
    def test_sales_invoice_on_submit(self):
        with patch("tims_incortex.tims_incortex.api.sales_invoice.get_hs_code_before_save"):
            # Create customer
            if not frappe.db.exists("Customer", "Test Customer"):
                frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": "Test Customer",
                    "customer_group": "Individual",
                    "territory": "All Territories"
                }).insert(ignore_permissions=True)

            # Create item
            if not frappe.db.exists("Item", "Test Service Item"):
                frappe.get_doc({
                    "doctype": "Item",
                    "item_code": "Test Service Item",
                    "item_name": "Test Service Item",
                    "item_group": "Services",
                    "stock_uom": "Nos",
                    "is_sales_item": 1
                }).insert(ignore_permissions=True)

            # Create Sales Invoice
            sales_invoice = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": "Test Customer",
                "posting_date": nowdate(),
                "items": [
                    {
                        "item_code": "Test Service Item",
                        "qty": 1,
                        "rate": 100
                    }
                ]
            })
            sales_invoice.insert(ignore_permissions=True)
            sales_invoice.submit()

            self.assertEqual(sales_invoice.docstatus, 1)