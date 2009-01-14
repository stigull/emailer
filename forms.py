#coding: utf-8
import django.forms as forms
from django.template.loader import render_to_string
from django.db.models.loading import get_model
from django.shortcuts import render_to_response

from emailer.classes import Emailer

class ModelNotFoundError(Exception):
    def __init__(self, appname, modelname):
        super(ModelNotFoundError, self).__init__("The model '%s' was not found in application '%s" % (modelname, appname))

class ObjectToSendWrapper(object):
    def __init__(self, instance):
        self.instance = instance

    def get_email_subject(self):
        raise NotImplementedError()

    def get_email_template(self):
        raise NotImplementedError()

    def get_email_context(self):
        raise NotImplementedError()

    def get_email_recipients(self):
        raise NotImplementedError()

class EmailObjectFormFactory(object):

    def __init__(self, post_data, emailer = None):
        if emailer is None:
            emailer = Emailer()
        self.emailer = emailer
        self.post_data = post_data

    def get_form(self):
        if 'wrapped_appname' in self.post_data and 'wrapped_classname' in self.post_data:
            return EmailWrappedObjectForm(emailer = self.emailer, data = self.post_data)
        else:
            return EmailObjectForm(emailer = self.emailer, data = self.post_data)

class EmailObjectForm(forms.Form):
    """
    The model that should be sent as an email must implement the following methods:
        get_email_subject() - should return the subject of the email
        get_email_template() - should return a path to a template
        get_email_template_context() - should return a dictionary. The template will be rendered within this context
        get_email_recipients() - shoult return a list of emails.
        [process_pre_email() - An optional method for any instance processing]
    """

    appname = forms.CharField(max_length = 100, widget = forms.HiddenInput)
    modelname = forms.CharField(max_length = 200, widget = forms.HiddenInput)
    instance_id = forms.IntegerField(widget = forms.HiddenInput)

    def __init__(self, emailer = None, *args, **kwargs):
        super(EmailObjectForm, self).__init__(*args, **kwargs)
        self.emailer = emailer

    def render(self, legend, submit_label):
        return render_to_string('emailer/email_object_form.html', {'form': self,
                                                                    'legend': legend,
                                                                    'submit_label': submit_label})

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
            self.process_instance(instance)
            subject = instance.get_email_subject()
            template = instance.get_email_template()
            context = instance.get_email_context()
            recipients = instance.get_email_recipients()
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


class EmailWrappedObjectForm(EmailObjectForm):
    wrapped_appname = forms.CharField(max_length = 100, widget = forms.HiddenInput)
    wrapped_classname = forms.CharField(max_length = 100, widget = forms.HiddenInput)

    def __init_(self, *args, **kwargs):
        super(EmailWrappedObjectForm, self).__init__(self, *args, **kwargs)

    def get_wrapper(self):
        """
        Pre:    self.is_valid() is True
        """
        appnames = self.cleaned_data['wrapped_appname'].split(".")
        classname = self.cleaned_data['wrapped_classname']
        module = __import__(appnames[0])
        for submodulename in appnames[1:]:
            module = getattr(module, submodulename)
        return getattr(module, classname)

    def get_instance(self):
        instance = super(EmailWrappedObjectForm, self).get_instance()
        Wrapper = self.get_wrapper()
        return Wrapper(instance)

