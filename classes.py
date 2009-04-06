from django.template.loader import render_to_string
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings

class Emailer(object):
    def __init__(self, from_email = None):
        if from_email is None:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL")
        self.from_email = from_email

    def send_single_email(self, to, subject, template, context):
        raise NotImplementedError()

    def send_email(self, to, subject, template, context):
        body = render_to_string(template, context)

        print to, subject, body
        raise NotImplementedError()

    def send_mass_mail(self, to, subject, template, context):
        datalist = []
        body = render_to_string(template, context)
        for email in to:
            datalist.append((subject, body, self.from_email, [email]))
        datatuple = tuple(datalist)
        try:
            send_mass_mail(datatuple, fail_silently=False)
            return True
        except Exception, e:
            print e
            return False