from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from emailer.forms import EmailObjectForm, EmailObjectFormFactory

def send_object(request):
    if request.method == "POST":
        factory = EmailObjectFormFactory(request.POST)
        form = factory.get_form()
        if form.is_valid():
            return form.process()

    return HttpResponseRedirect(reverse("index"))