# Copyright (c) 2021, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

class UserRectificationRequest(WebsiteGenerator):
	def before_submit(self):
	    doc = frappe.get_doc({'doctype': 'Rectification Request', 'request_for': self.name})
	    doc.insert()