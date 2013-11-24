import django_filters
import models

class MunicipalityFilter(django_filters.FilterSet):
    province = django_filters.CharFilter(name="province__name", lookup_type="iexact")

    class Meta:
        model = models.Municipality
        fields = ['province']

class WardFilter(django_filters.FilterSet):
    municipality = django_filters.CharFilter(name="municipality__pk")
    province = django_filters.CharFilter(name="municipality__province__name", lookup_type="iexact")

    class Meta:
        model = models.Ward
        fields = [
            'municipality', 'province'
        ]


class VotingDistrictFilter(django_filters.FilterSet):
    ward = django_filters.CharFilter(name="ward__code")
    municipality = django_filters.CharFilter(name="ward__municipality__pk")
    province = django_filters.CharFilter(name="ward__municipality__province__name", lookup_type="iexact")

    class Meta:
        model = models.VotingDistrict
        fields = [
            'ward', 'municipality', 'province'
        ]

class ResultFilter(django_filters.FilterSet):
    voting_district = django_filters.CharFilter(name="voting_district__code")
    ward = django_filters.CharFilter(name="voting_district__ward__code")
    municipality = django_filters.CharFilter(name="voting_district__ward__municipality__pk")
    province = django_filters.CharFilter(name="voting_district__ward__municipality__province__name", lookup_type="iexact")
    party = django_filters.CharFilter(name="party__name", lookup_type="iexact")

    max_votes = django_filters.NumberFilter(name="votes", lookup_type="lte")
    min_votes = django_filters.NumberFilter(name="votes", lookup_type="gte")

    class Meta:
        model = models.Result
        fields = [
            'votes', 'max_votes', 'min_votes',
            'party',
            'voting_district', 'ward', 'municipality', 'province'
        ]

class ResultSummaryFilter(django_filters.FilterSet):
    voting_district = django_filters.CharFilter(name="voting_district__code")
    ward = django_filters.CharFilter(name="voting_district__ward__code")
    municipality = django_filters.CharFilter(name="voting_district__ward__municipality__pk")
    province = django_filters.CharFilter(name="voting_district__ward__municipality__province__name", lookup_type="iexact")

    max_total_votes = django_filters.NumberFilter(name="total_votes", lookup_type="lte")
    min_total_votes = django_filters.NumberFilter(name="total_votes", lookup_type="gte")
    max_spoilt_votes = django_filters.NumberFilter(name="spoilt_votes", lookup_type="lte")
    min_spoilt_votes = django_filters.NumberFilter(name="spoilt_votes", lookup_type="gte")
    max_registered_voters = django_filters.NumberFilter(name="registered_voters", lookup_type="lte")
    min_registered_voters = django_filters.NumberFilter(name="registered_voters", lookup_type="gte")
    max_special_votes = django_filters.NumberFilter(name="special_votes", lookup_type="lte")
    min_special_votes = django_filters.NumberFilter(name="special_votes", lookup_type="gte")
    max_voter_turnout_perc = django_filters.NumberFilter(name="voter_turnout_perc", lookup_type="lte")
    min_voter_turnout_perc = django_filters.NumberFilter(name="voter_turnout_perc", lookup_type="gte")
    max_section_24a_votes = django_filters.NumberFilter(name="section_24a_votes", lookup_type="lte")
    min_section_24a_votes = django_filters.NumberFilter(name="section_24a_votes", lookup_type="gte")

    class Meta:
        model = models.ResultSummary
        fields = [
            'total_votes', 'max_total_votes', 'min_total_votes',
            'spoilt_votes', 'max_spoilt_votes', 'min_spoilt_votes',
            'registered_voters', 'max_registered_voters', 'min_registered_voters',
            'special_votes', 'max_special_votes', 'min_special_votes',
            'voter_turnout_perc', 'max_voter_turnout_perc', 'min_voter_turnout_perc',
            'section_24a_votes', 'max_section_24a_votes', 'min_section_24a_votes',
            'voting_district', 'ward', 'municipality', 'province'
        ]

