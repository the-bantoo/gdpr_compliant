import frappe
from frappe import _
from frappe.utils import nowdate, add_years, add_days, today
from datetime import datetime
 
def p(*args):
    if testing():
        print(*args)


# run once a day
@frappe.whitelist()
def process_requests():
    #frappe.get_list("Request", filters={})

    settings = frappe.get_cached_doc("GDPR Settings")

    current_date = nowdate()
    server_name = frappe.utils.get_url()

    five_years_ago = add_years(current_date, -5)

    yy_year = today()[2:4]
    
    request_entries = frappe.get_all('Request', fields={'*'}, filters={
            'gdpr_compliance_update': ['<=', five_years_ago], 
        })

    if testing():
        five_years_ago = add_years(current_date, 0) #-5 # dev
    
        request_entries = frappe.get_all('Request', fields={'*'}, limit=2, filters={
            'gdpr_compliance_update': ['<=', five_years_ago],
            'email_address': 'adam.daveed@gmail.com'
        })

    p('five_years_ago', five_years_ago)
    

    for r in request_entries:
        """ get term compliances newer than 5 years old"""
        p(r.full_name)

        request_has_valid_terms = frappe.db.exists("Term Compliance", { 
            'status': ['in', ['New','Unresponsive', 'Extend', 'Extended', 'Erasure Requested']],
            'creation': ['>=', five_years_ago],
            'request': r.name
        })

        if not request_has_valid_terms:
            # create term

            email_actions = """
                        <div class="row justify-content-center">
                            <div class="btn-group" role="group" aria-label="Data storage term extension">
                                <a href="{server_name}/term-compliance?term={name}&action=erase" style="text-decoration: none;" class="btn btn-secondary">Erase</a>
                                <a href="{server_name}/term-compliance?term={name}&action=extend" style="text-decoration: none;" class="btn btn-primary">Extend</a>
                            </div>
                        </div>
            """.format(server_name=server_name, name=r.name+'-'+yy_year)
            
            r.update({'email_actions': email_actions})

            doc = frappe.get_doc({
                'request': r.name,
                'doctype': 'Term Compliance',
                'status': "New",
                'email': settings.template.format(**r)
            })

            doc.insert(ignore_permissions=True)
            doc.submit() # dev

    if testing():
        frappe.enqueue(
            queue="short",
            method="gdpr_compliant.app.process_terms",
            now=True
        )

def testing():
    settings = frappe.get_cached_doc("GDPR Settings")

    if settings.testing_mode == 1:
        return True
    else:
        return False



# runs every 1 hr
def process_terms():

    settings = frappe.get_cached_doc("GDPR Settings")

    current_date = nowdate()
    five_years_ago = add_years(current_date, -5)
    
    if testing():
        five_years_ago = add_years(current_date, 1) #-5 dev


    terms = frappe.get_list("Term Compliance", fields={"*"}, order_by="creation desc",filters={
                'status': ['in', ['New', 'Unresponsive', 'Extend', 'Erase']]
            })

    for term in terms:

        request = frappe.get_doc("Request", term.name[:-3])

        if term.status == "New":
            send_mail(term, request, settings)
            update_term(term, "Unresponsive", increase_sent=True)

        elif term.status == "Extend":
            extend(term)

        elif term.status == "Erase":
            erase(term, request)

        elif term.status == "Unresponsive":

            # compare last email date to email frequency and send another email
            next_email_date = add_days(term.last_email_date, int(settings.days_to_repeat))

            #p(type(next_email_date))
            if next_email_date.__class__.__name__ == "datetime.datetime":
                next_email_date = next_email_date.date();

            if str(next_email_date) == str(current_date):
                p('date_to_email', next_email_date, 'current_date', current_date)

                if settings.max_repeats <= term.emails_sent:
                    p('max_repeats')

                    # default action
                    if settings.unresponsive_default == 'Erase':
                        erase(term, request)
                    else:
                        extend(term)

                else:
                    # send email, update term
                    p('not max_repeats')
                    send_mail(term, request, settings)
                    update_term(term, "Unresponsive", increase_sent=True)
    
    p(five_years_ago)

def erase(term, request):
    p("erase")
    # create erasure request
    # update status of tc
    # update_request(term) after erasure request is carried out

    doc = frappe.get_doc({
            'doctype': 'Erasure Request',
            'first_name': request.first_name,
            'last_name': request.last_name,
            'full_name': request.full_name,
            'email_address': request.email_address,
            'message': """This Erasure Request was automatically generated by the system because {first_name} has been on the system for 5 years and has either not given approval to keep their data or has opted this erasure.""".format(first_name=request.first_name)
        })
    doc.insert(ignore_permissions=True)
    
    update_term(term, "Erasure Requested")

def extend(term):
    p("extend")
    # update to extend
    update_term(term, "Extended")
    update_request(term)

def send_mail(term, request, settings):
    
    p("send_mail")

    frappe.enqueue(
        queue="short",
        method=frappe.sendmail,
        recipients=request.email_address,
        sender=settings.email_sender,
        subject=settings.email_subject,
        message=term.email,
        #now=True,
        reference_doctype="Term Compliance",
        reference_name=term.name
    )


def update_term(term, next_status, increase_sent=None):
    doc = frappe.get_doc("Term Compliance", term.name)
    doc.status = next_status
    if increase_sent:
        doc.emails_sent = (term.emails_sent) + 1
        doc.last_email_date = today()
    
    doc.save(ignore_permissions=True)
    doc.notify_update()

    p("updated_term")


@frappe.whitelist(allow_guest=True)
def update_term_from_api(data):

    if frappe.db.exists("Term Compliance", data.get('term')):
            
        doc = frappe.get_doc("Term Compliance", data.term)
        doc.status = "Erase"

        if data.action == "extend":
            doc.status = "Extend"
            
        doc.save(ignore_permissions=True)
        doc.notify_update()

        frappe.db.commit()

        update_request(data.term)

        p(data)
        p(doc.status)


def update_request(term):
    frappe.set_value("Request", term.name[:-3], 'gdpr_compliance_update', today())