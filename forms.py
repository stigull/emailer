import django.forms as forms
from django.template.loader import render_to_string
from django.db.models.loading import get_model
from django.shortcuts import render_to_response

from emailer.classes import Emailer

class ModelNotFoundError(Exception):
    def __init__(appname, modelname):
        super(ModelNotFoundError, self).__init__("The model '%s' was not found in application '%s" % (modelname, appname))

class EmailObjectForm(forms.Form):
    """
    The model that should be sent as an email must implement the following methods:
        get_email_subject() - should return the subject of the email
        get_email_template() - should return a path to a template
        get_email_template_context() - should return a dictionary. The template will be rendered within this context
        get_email_recipients() - shoult return a list of emails.
    """

    appname = forms.CharField(max_length = 100, widget = forms.HiddenInput)
    modelname = forms.CharField(max_length = 200, widget = forms.HiddenInput)
    instance_id = forms.IntegerField(widget = forms.HiddenInput)

    def render(self):
        return render_to_string('emailer/email_object_form.html', {'form': self })

    def process(self):
        """
        Pre:    self.is_valid() is True
        """
        try:
            instance = self.get_instance()
        except ModelNotFoundError, e:
            #TODO:
            print e
        else:
            emailer = Emailer()
            subject = instance.get_email_subject()
            template = instance.get_email_template()
            context = instance.get_email_context()
            recipients = instance.get_email_recipients()
            did_succeed = emailer.send_mass_mail(recipients, subject, template, context)
            return self.create_response(subject, template, context, recipients, did_succeed)

    def create_response(self, subject, template, context, recipients, did_succeed):
        context['email_subject'] = subject
        context['email_body'] = render_to_string(template, context)
        context['email_recipients'] = recipients
        context['email_did_succeed'] = did_succeed
        return render_to_response('emailer/email_response.html', context)

    def get_instance(self):
        """
        Pre:    self.is_valid() is True
        """

        appname = self.cleaned_data['appname']
        modelname = self.cleaned_data['modelname']
        instance_id = self.cleaned_data['instance_id']
        Model = get_model(appname, modelname)
        if Model is not None:
            return Model.objects.get(id = instance_id)
        else:
            raise ModelNotFoundError(appname, modelname)
