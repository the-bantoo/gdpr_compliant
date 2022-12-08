import frappe
from frappe import _
from frappe.utils import today
from gdpr_compliant.app import update_term_from_api

def get_context(context):
    context.name = "Administrator"
    data = frappe.form_dict

    if (not data.get('term') or data.get('term') == "") or (not data.get('term') or data.get('action') == ""):
        return
    
    update_term_from_api(data)


def p(*args):
    print(*args)
