# Copyright (c) 2025, solidad kimeu and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Custom Item", "width": 140},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Custom Warehouse", "width": 140},
        {"label": "Qty", "fieldname": "qty_after_transaction", "fieldtype": "Float", "width": 100},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Stock Value", "fieldname": "stock_value", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters):
    conditions = []
    if filters.get("as_on_date"):
        conditions.append("posting_datetime <= %(as_on_date)s")
    if filters.get("item_code"):
        conditions.append("item_code = %(item_code)s")
    if filters.get("warehouse"):
        conditions.append("warehouse = %(warehouse)s")

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = "WHERE " + condition_str

    results = frappe.db.sql(f"""
        SELECT
            sle.item_code,
            sle.warehouse,
            sle.qty_after_transaction,
            sle.valuation_rate,
            sle.stock_value
        FROM `tabCustom Stock Ledger Entry` sle
        INNER JOIN (
            SELECT item_code, warehouse, MAX(posting_datetime) as latest_time
            FROM `tabCustom Stock Ledger Entry`
            {condition_str}
            GROUP BY item_code, warehouse
        ) latest
        ON sle.item_code = latest.item_code 
           AND sle.warehouse = latest.warehouse 
           AND sle.posting_datetime = latest.latest_time
    """, filters, as_dict=True)

    return results
