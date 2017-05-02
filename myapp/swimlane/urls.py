from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^upload/$', views.upload),
    url(r'^handle_file_upload/$', views.handle_file_upload),
    url(r'^results/$', views.results),
    url(r'^text_file_detail/(?P<file_id>[\w-]+)/$', views.file_detail),
    url(r'^ip_detail/(?P<ip>[0-9.]+)/$', views.ip_detail),
]
