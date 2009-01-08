from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from emailer.forms import EmailObjectForm

def send_object(request):
    if request.method == "POST":
        form = EmailObjectForm(request.POST)
        if form.is_valid():
            return form.process()

    return HttpResponseRedirect(reverse("index"))