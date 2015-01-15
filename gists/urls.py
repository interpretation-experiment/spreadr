from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from gists import views


urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^sentences/$',
        views.SentenceList.as_view(),
        name='sentence-list'),
    url(r'^sentences/(?P<pk>[0-9]+)/$',
        views.SentenceDetail.as_view(),
        name='sentence-detail'),
    url(r'^users/$',
        views.UserList.as_view(),
        name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$',
        views.UserDetail.as_view(),
        name='user-detail'),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]


urlpatterns = format_suffix_patterns(urlpatterns)
