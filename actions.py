from django.template.loader import render_to_string
from django.shortcuts import render_to_response

from emailer.classes import Emailer

class SendAction(object):
    def __init__(self, request, queryset):
        self.emailer = Emailer()
        self.request = request
        self.instance = queryset[0]

    def process(self):
        self.process_instance(self.instance)
        subject = self.instance.get_email_subject()
        template = self.instance.get_email_template()
        context = self.instance.get_email_context()
        recipients = self.instance.get_email_recipients()
        did_succeed = self.emailer.send_mass_mail(recipients, subject, template, context)
        return self.create_response(subject, template, context, recipients, did_succeed)

    def create_response(self, subject, template, context, recipients, did_succeed):
        context['email_subject'] = subject
        context['email_body'] = render_to_string(template, context)
        context['email_recipients'] = recipients
        context['email_did_succeed'] = did_succeed
        return render_to_response('emailer/email_response.html', context)

    def process_instance(self, instance):
        try:
            instance.process_pre_email()
        except AttributeError,e:
            print e