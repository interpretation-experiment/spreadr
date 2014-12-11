from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from gists import views


urlpatterns = [
    url(r'^sentences/$', views.SentenceList.as_view()),
    url(r'^sentences/(?P<pk>[0-9]+)/$', views.SentenceDetail.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
