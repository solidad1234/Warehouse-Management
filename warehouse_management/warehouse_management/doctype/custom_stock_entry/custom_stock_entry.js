// Copyright (c) 2025, solidad kimeu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custom Stock Entry', {
    source_warehouse(frm) {
        frm.doc.items.forEach(row => {
            row.source_warehouse = frm.doc.source_warehouse;
        });
        frm.refresh_field('items');
    },

    target_warehouse(frm) {
        frm.doc.items.forEach(row => {
            row.target_warehouse = frm.doc.target_warehouse;
        });
        frm.refresh_field('items');
    }
});

frappe.ui.form.on('Custom Stock Entry Item', {
    items_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.source_warehouse = frm.doc.source_warehouse;
        row.target_warehouse = frm.doc.target_warehouse;
        frm.refresh_field('items');
    }
});
