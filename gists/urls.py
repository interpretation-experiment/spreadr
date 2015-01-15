from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from gists import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'sentences', views.SentenceViewSet)
router.register(r'users', views.UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]


#urlpatterns = format_suffix_patterns(urlpatterns)
