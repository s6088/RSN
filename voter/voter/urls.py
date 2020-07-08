from django.contrib import admin
from django.urls import re_path

from .views import home_view, submit_vote

urlpatterns = [
    re_path(r'^$', home_view, name='home'),
    re_path(r'^submit$', submit_vote, name='submit'),
]
