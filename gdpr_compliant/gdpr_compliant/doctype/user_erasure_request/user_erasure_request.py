# Copyright (c) 2021, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UserErasureRequest(Document):
    def before_submit(self):
	    doc = frappe.get_doc({'doctype': 'Erasure Request', 'request_for': self.name})
	    doc.insert()