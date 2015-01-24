from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from gists import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'trees', views.TreeViewSet)
router.register(r'sentences', views.SentenceViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
