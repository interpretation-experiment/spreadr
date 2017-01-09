from django.db.models import Count
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
    branches_count_gte = django_filters.MethodFilter()
    branches_count_lte = django_filters.MethodFilter()
    shortest_branch_depth_gte = django_filters.MethodFilter()
    shortest_branch_depth_lte = django_filters.MethodFilter()

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

    def filter_branches_count(self, queryset, value, tipe):
        if tipe not in ['lte', 'gte']:
            raise ValueError("Unknown comparison type: '{}'".format(tipe))

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

    def filter_shortest_branch_depth(self, queryset, value, tipe):
        if tipe == 'lte':
            def condition(d):
                return d <= ivalue
        elif tipe == 'gte':
            def condition(d):
                return d >= ivalue
        else:
            raise ValueError("Unknown comparison type: '{}'".format(tipe))

        try:
            ivalue = int(value)
        except ValueError:
            return queryset

        pks = [tree.pk for tree in queryset
               if condition(tree.shortest_branch_depth)]
        return queryset.filter(pk__in=pks)

    def filter_shortest_branch_depth_gte(self, queryset, value):
        return self.filter_shortest_branch_depth(queryset, value, 'gte')

    def filter_shortest_branch_depth_lte(self, queryset, value):
        return self.filter_shortest_branch_depth(queryset, value, 'lte')

    class Meta:
        model = Tree
        fields = (
            'profile',
            'root_language',
            'root_bucket',
            'untouched_by_profile',
            'with_other_mothertongue',
            'without_other_mothertongue',
            'branches_count_gte', 'branches_count_lte',
            'shortest_branch_depth_gte', 'shortest_branch_depth_lte',
        )
