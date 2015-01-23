from random import sample

from rest_framework import filters
from django.conf import settings


class SampleFilterBackend(filters.BaseFilterBackend):
    """
    Sample `page_size` items from the queryset if the `sample` keyword is present.
    """
    def filter_queryset(self, request, queryset, view):
        if request.QUERY_PARAMS.get('sample', None) == '':
            return self.sample(request, queryset)
        else:
            return queryset

    @classmethod
    def sample(self, request, instance):
        # Determine how many sentences to return
        paginate_by = settings.REST_FRAMEWORK.get('PAGINAGE_BY', 10)
        max_paginate_by = settings.REST_FRAMEWORK.get('MAX_PAGINAGE_BY', 100)
        page_size = int(request.QUERY_PARAMS.get('page_size', paginate_by))
        count = instance.count()
        if page_size > max_paginate_by:
            page_size = max_paginate_by
        if page_size > count:
            page_size = count

        # Sample
        pks = [d['pk'] for d in instance.values('pk')]
        sampled_pks = sample(pks, page_size)
        return instance.filter(pk__in=sampled_pks)
