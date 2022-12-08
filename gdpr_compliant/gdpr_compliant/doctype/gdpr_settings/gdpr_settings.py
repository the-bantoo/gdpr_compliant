# Copyright (c) 2022, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document, _

class GDPRSettings(Document):
	def before_save(self):
		try:
			request_entries = frappe.get_all('Request', fields={'*'}, limit=1)

			for r in request_entries:
				r.update({'email_actions': 'email_actions'})
				self.template.format(**r)

		except KeyError as e:
			frappe.throw(title="Invalid Field", msg=_("The Request doctype does not contain a field called ") + str(e))

