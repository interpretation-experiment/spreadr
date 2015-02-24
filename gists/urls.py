from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter

from gists import views


# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'trees', views.TreeViewSet)
router.register(r'sentences', views.SentenceViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^meta/$', views.Meta.as_view(), name='meta'),
    url(r'^$', views.APIRoot.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
