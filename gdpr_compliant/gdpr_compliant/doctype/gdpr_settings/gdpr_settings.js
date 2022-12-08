// Copyright (c) 2022, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on('GDPR Settings', {
	/**refresh: function(frm) {
		frappe.call({
			method: "gdpr_compliant.app.process_requests",
			callback: function(r) {
				console.log(r.message)
			}
		});
	}
	*/
});
