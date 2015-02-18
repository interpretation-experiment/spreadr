import django_filters

from gists.models import Profile, Tree, LANGUAGE_CHOICES


class TreeFilter(django_filters.FilterSet):
    root_language = django_filters.ChoiceFilter(name='root__language',
                                                choices=LANGUAGE_CHOICES)
    untouched_by_profile = django_filters.MethodFilter(
        action='filter_untouched_by_profile')

    def filter_untouched_by_profile(self, queryset, value):
        try:
            profile = Profile.objects.get(pk=value)
            return queryset.exclude(
                pk__in=profile.trees.values_list('pk', flat=True))
        except Profile.DoesNotExist:
            return queryset

    class Meta:
        model = Tree
        fields = (
            'root_language',
            'untouched_by_profile',
        )
