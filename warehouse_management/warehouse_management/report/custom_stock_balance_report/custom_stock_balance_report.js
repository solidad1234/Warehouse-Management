// Copyright (c) 2025, solidad kimeu and contributors
// For license information, please see license.txt

frappe.query_reports["Custom Stock Balance Report"] = {
    "filters": [
        {
            fieldname: "as_on_date",
            label: "As on Date",
            fieldtype: "Date",
            // default: frappe.datetime.get_today(),
            reqd: 0
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
