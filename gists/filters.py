import django_filters

from gists.models import (Profile, Tree, LANGUAGE_CHOICES, OTHER_LANGUAGE,
                          BUCKET_CHOICES)


class TreeFilter(django_filters.FilterSet):
    profile = django_filters.MethodFilter()
    root_language = django_filters.ChoiceFilter(name='root__language',
                                                choices=LANGUAGE_CHOICES)
    root_bucket = django_filters.ChoiceFilter(name='root__bucket',
                                              choices=BUCKET_CHOICES)
    untouched_by_profile = django_filters.MethodFilter()
    with_other_mothertongue = django_filters.MethodFilter()
    without_other_mothertongue = django_filters.MethodFilter()

    def filter_profile(self, queryset, value):
        try:
            profile = Profile.objects.get(pk=value)
            return queryset.filter(profiles=profile).distinct()
        except Profile.DoesNotExist:
            return queryset

    def filter_untouched_by_profile(self, queryset, value):
        try:
            profile = Profile.objects.get(pk=value)
            return queryset.exclude(
                pk__in=profile.trees.values_list('pk', flat=True))
        except Profile.DoesNotExist:
            return queryset

    def filter_with_other_mothertongue(self, queryset, value):
        bvalue = value.lower() == 'true'
        if bvalue:
            return queryset.filter(profiles__mothertongue=OTHER_LANGUAGE)
        else:
            return queryset

    def filter_without_other_mothertongue(self, queryset, value):
        bvalue = value.lower() == 'true'
        if bvalue:
            return queryset.exclude(profiles__mothertongue=OTHER_LANGUAGE)
        else:
            return queryset

    class Meta:
        model = Tree
        fields = (
            'profile',
            'root_language',
            'root_bucket',
            'untouched_by_profile',
            'with_other_mothertongue',
            'without_other_mothertongue',
        )
