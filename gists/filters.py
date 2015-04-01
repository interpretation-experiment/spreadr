from django.db.models import Count
import django_filters

from gists.models import Profile, Tree, LANGUAGE_CHOICES, OTHER_LANGUAGE


class TreeFilter(django_filters.FilterSet):
    root_language = django_filters.ChoiceFilter(name='root__language',
                                                choices=LANGUAGE_CHOICES)
    untouched_by_profile = django_filters.MethodFilter(
        action='filter_untouched_by_profile')
    with_other_mothertongue = django_filters.MethodFilter(
        action='filter_with_other_mothertongue')
    without_other_mothertongue = django_filters.MethodFilter(
        action='filter_without_other_mothertongue')
    branches_count_gte = django_filters.MethodFilter(
        action='filter_branches_count_gte')
    branches_count_lte = django_filters.MethodFilter(
        action='filter_branches_count_lte')

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

    def filter_branches_count(self, queryset, value, tipe):
        try:
            ivalue = int(value)
        except ValueError:
            return queryset

        qs = queryset.annotate(branches_count=Count('root__children'))
        return qs.filter(**{'branches_count__' + tipe: ivalue})

    def filter_branches_count_gte(self, queryset, value):
        return self.filter_branches_count(queryset, value, 'gte')

    def filter_branches_count_lte(self, queryset, value):
        return self.filter_branches_count(queryset, value, 'lte')

    class Meta:
        model = Tree
        fields = (
            'root_language',
            'untouched_by_profile',
            'with_other_mothertongue',
            'without_other_mothertongue',
        )
