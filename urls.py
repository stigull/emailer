#! /usr/bin/env python
# -*- coding: utf8 -*-

from django.conf.urls.defaults import *

from emailer.views import send_object

urlpatterns = patterns('',
    url(r'senda-akvedinn-hlut/$', send_object , name = 'email-object'),
)
