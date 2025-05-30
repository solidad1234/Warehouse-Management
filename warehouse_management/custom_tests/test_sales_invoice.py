import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, today
from unittest.mock import patch, Mock, MagicMock
import json
from tims_incortex.tims_incortex.api.sales_invoice import (
    TimsInvoice, 
    sign_single_invoice, 
    retry_pending_invoices,
    get_qr_code,
    format_invoice_number,
    currency_code,
    is_valid_kra_pin,
    before_save,
    prevent_cancel_signed_invoice,
    get_invoice
)

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

class TestTimsInvoice(FrappeTestCase):
    def setUp(self):
        # Create test company
        if not frappe.db.exists("Company", "Test Company"):
            frappe.get_doc({
                "doctype": "Company",
                "company_name": "Test Company",
                "default_currency": "KES"
            }).insert(ignore_permissions=True)
        
        # Create test customer
        if not frappe.db.exists("Customer", "Test TIMS Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test TIMS Customer",
                "customer_group": "Individual",
                "territory": "All Territories",
                "tax_id": "A123456789B"
            }).insert(ignore_permissions=True)
        
        # Create test item
        if not frappe.db.exists("Item", "Test TIMS Item"):
            frappe.get_doc({
                "doctype": "Item",
                "item_code": "Test TIMS Item",
                "item_name": "Test TIMS Item",
                "item_group": "Services",
                "stock_uom": "Nos",
                "is_sales_item": 1
            }).insert(ignore_permissions=True)
        
        # Create test sales invoice
        self.sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test TIMS Customer",
            "company": "Test Company",
            "posting_date": nowdate(),
            "currency": "KES",
            "tax_id": "A123456789B",
            "items": [
                {
                    "item_code": "Test TIMS Item",
                    "qty": 2,
                    "rate": 100,
                    "custom_hs_code": "123456"
                }
            ]
        })
        self.sales_invoice.insert(ignore_permissions=True)

    @patch('tims_incortex.tims_incortex.api.sales_invoice.get_tims_settings')
    def test_tims_invoice_init(self, mock_settings):
        mock_settings.return_value = {
            'api_url': 'https://api.test.com/',
            'api_key': 'test_key',
            'company_pin': 'P123456789A'
        }
        
        tims_invoice = TimsInvoice(self.sales_invoice.name, "Test Company")
        self.assertEqual(tims_invoice.invoice.name, self.sales_invoice.name)
        self.assertIsNotNone(tims_invoice.settings)

    @patch('tims_incortex.tims_incortex.api.sales_invoice.get_tims_settings')
    def test_sign_invoice_already_signed(self, mock_settings):
        mock_settings.return_value = {
            'api_url': 'https://api.test.com/',
            'api_key': 'test_key',
            'company_pin': 'P123456789A'
        }
        
        # Set invoice as already signed
        frappe.db.set_value("Sales Invoice", self.sales_invoice.name, "etr_invoice_number", "ETR123456")
        
        tims_invoice = TimsInvoice(self.sales_invoice.name, "Test Company")
        
        with patch('frappe.msgprint') as mock_msgprint:
            tims_invoice.sign_invoice()
            mock_msgprint.assert_called_with("Invoice already signed.", alert=True)

    @patch('tims_incortex.tims_incortex.api.sales_invoice.get_tims_settings')
    def test_sign_invoice_opening_invoice(self, mock_settings):
        mock_settings.return_value = {
            'api_url': 'https://api.test.com/',
            'api_key': 'test_key',
            'company_pin': 'P123456789A'
        }
        
        # Set invoice as opening
        frappe.db.set_value("Sales Invoice", self.sales_invoice.name, "is_opening", "Yes")
        
        tims_invoice = TimsInvoice(self.sales_invoice.name, "Test Company")
        
        with patch('frappe.msgprint') as mock_msgprint:
            tims_invoice.sign_invoice()
            mock_msgprint.assert_called_with("Opening invoices cannot be signed.", alert=True)

    @patch('tims_incortex.tims_incortex.api.sales_invoice.get_tims_settings')
    def test_prepare_payload(self, mock_settings):
        mock_settings.return_value = {
            'api_url': 'https://api.test.com/',
            'api_key': 'test_key',
            'company_pin': 'P123456789A'
        }
        
        tims_invoice = TimsInvoice(self.sales_invoice.name, "Test Company")
        
        with patch('tims_incortex.tims_incortex.api.sales_invoice.get_relevant_invoice_number', return_value=""):
            payload = tims_invoice._prepare_payload()
        
        self.assertIn('invoice_date', payload)
        self.assertIn('invoice_number', payload)
        self.assertIn('customer_pin', payload)
        self.assertIn('items_list', payload)
        self.assertEqual(payload['invoice_pin'], 'P123456789A')

class TestUtilityFunctions(FrappeTestCase):
    
    def test_currency_code_kes(self):
        result = currency_code("KES")
        self.assertEqual(result, "Ksh")
    
    def test_format_invoice_number(self):
        result = format_invoice_number("INV-2024-001")
        self.assertEqual(result, "INV2024001")
        
        result = format_invoice_number("INV@#$123")
        self.assertEqual(result, "INV123")
    
    def test_is_valid_kra_pin_valid(self):
        self.assertTrue(is_valid_kra_pin("A123456789B"))
        self.assertTrue(is_valid_kra_pin("P987654321X"))
    
    def test_is_valid_kra_pin_invalid(self):
        self.assertFalse(is_valid_kra_pin("123456789"))  
        self.assertFalse(is_valid_kra_pin("AB123456789"))  
        self.assertFalse(is_valid_kra_pin("A12345678B"))  
        self.assertFalse(is_valid_kra_pin("1123456789B"))  
    
    def test_get_qr_code(self):
        result = get_qr_code("https://test.com")
        self.assertTrue(result.startswith("data:image/png;base64,"))

class TestDocumentEvents(FrappeTestCase):
    
    def setUp(self):
        # Create test customer
        if not frappe.db.exists("Customer", "Test Customer Events"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer Events",
                "customer_group": "Individual",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)
    
    def test_before_save_invalid_kra_pin(self):
        doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Customer Events",
            "tax_id": "invalid_pin",
            "posting_date": nowdate(),
            "items": []
        })
        
        with patch('tims_incortex.tims_incortex.api.sales_invoice.get_hs_code_before_save'):
            with self.assertRaises(frappe.ValidationError):
                before_save(doc, None)
    
    def test_prevent_cancel_signed_invoice(self):
        doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Customer Events",
            "custom_signing_status": "Signed",
            "posting_date": nowdate(),
            "items": []
        })
        
        with self.assertRaises(frappe.ValidationError):
            prevent_cancel_signed_invoice(doc, None)

    def tearDown(self):
        # Clear test data
        frappe.db.rollback()