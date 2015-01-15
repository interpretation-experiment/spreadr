from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from gists import views


urlpatterns = [
    url(r'^sentences/$', views.SentenceList.as_view()),
    url(r'^sentences/(?P<pk>[0-9]+)/$', views.SentenceDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]


urlpatterns = format_suffix_patterns(urlpatterns)
