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
router.register(r'questionnaires', views.QuestionnaireViewSet)
router.register(r'word-spans', views.WordSpanViewSet,
                base_name='word-span')
router.register(r'comments', views.CommentViewSet)
router.register(r'emails', views.EmailAddressViewSet, base_name='email')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^meta/$', views.Meta.as_view(), name='meta'),
    url(r'^stats/$', views.Stats.as_view(), name='stats'),
    url(r'^$', views.APIRoot.as_view()),
    url(r'^confirm-email/(?P<key>\w+)/$', views.confirm_email,
        name='account_confirm_email')
]


urlpatterns = format_suffix_patterns(urlpatterns)
