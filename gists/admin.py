from django.contrib import admin

from solo.admin import SingletonModelAdmin
from gists.models import GistsConfiguration


admin.site.register(GistsConfiguration, SingletonModelAdmin)
