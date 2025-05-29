# Copyright (c) 2025, solidad kimeu and contributors
# For license information, please see license.txt


import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Time", "fieldname": "posting_time", "fieldtype": "Time", "width": 80},
        {"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Custom Item", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Custom Warehouse", "width": 140},
        {"label": "In Qty", "fieldname": "in_qty", "fieldtype": "Float", "width": 90},
        {"label": "Out Qty", "fieldname": "out_qty", "fieldtype": "Float", "width": 90},
        {"label": "Balance Qty", "fieldname": "qty_after_transaction", "fieldtype": "Float", "width": 120},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Stock Value", "fieldname": "stock_value", "fieldtype": "Currency", "width": 120},
        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 120},
        {"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 150},
    ]

def get_data(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    if filters.get("item_code"):
        conditions.append("item_code = %(item_code)s")
    if filters.get("warehouse"):
        conditions.append("warehouse = %(warehouse)s")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    entries = frappe.db.sql(f"""
        SELECT
            posting_date, posting_time, item_code, warehouse,
            IF(actual_qty > 0, actual_qty, 0) AS in_qty,
            IF(actual_qty < 0, -actual_qty, 0) AS out_qty,
            qty_after_transaction, valuation_rate, stock_value,
            voucher_type, voucher_no
        FROM `tabCustom Stock Ledger Entry`
        {where_clause}
        ORDER BY posting_datetime ASC
    """, filters, as_dict=True)

    return entries
