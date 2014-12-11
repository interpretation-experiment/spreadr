from django.conf.urls import url
from gists import views


urlpatterns = [
    url(r'^sentences/$', views.sentence_list),
    url(r'^sentences/(?P<pk>[0-9]+)/$', views.sentence_detail),
]
