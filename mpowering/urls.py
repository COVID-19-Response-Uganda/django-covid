# mpowering/urls.py
from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',

    url(r'^$', 'mpowering.views.home_view', name="mpowering_home"),
    
)
