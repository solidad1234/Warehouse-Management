// Copyright (c) 2025, solidad kimeu and contributors
// For license information, please see license.txt

frappe.query_reports["Custom Stock Ledger Report"] = {
    "filters": [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "item_code",
            label: "Item",
            fieldtype: "Link",
            options: "Custom Item",
            get_query: () => {
                return {
                    filters: {}
                };
            }
        },
        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Custom Warehouse",
            get_query: () => {
                return {
                    filters: {}
                };
            }
        }
    ]
};

