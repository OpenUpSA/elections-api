import models
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
import django_filters
import serializers

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer

class PartyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer

class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Province.objects.all()
    serializer_class = serializers.ProvinceSerializer
    filter_backends = (filters.DjangoFilterBackend,)

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.MunicipalitySerializer
    queryset = models.Municipality.objects.all()

    def get_queryset(self):
        queryset = models.Municipality.objects.all()
        province = self.request.QUERY_PARAMS.get('province', None)

        if province is not None:
            queryset = queryset.filter(province__name__iexact=province)
        return queryset

class WardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ward.objects.all()
    serializer_class = serializers.WardSerializer

    def get_queryset(self):
        queryset = models.Ward.objects.all()
        province = self.request.QUERY_PARAMS.get('province', None)
        municipality = self.request.QUERY_PARAMS.get('municipality', None)

        if province is not None:
            queryset = queryset.filter(municipality__province__name__iexact=province).distinct()
        if municipality is not None:
            queryset = queryset.filter(municipality__id=municipality)

        return queryset

class VotingDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.VotingDistrict.objects.all()
    serializer_class = serializers.VotingDistrictSerializer

    def get_queryset(self):
        queryset = models.VotingDistrict.objects.all()
        province = self.request.QUERY_PARAMS.get('province', None)
        municipality = self.request.QUERY_PARAMS.get('municipality', None)
        ward = self.request.QUERY_PARAMS.get('ward', None)

        if province is not None:
            queryset = queryset.filter(ward__municipality__province__name__iexact=province).distinct()
        if municipality is not None:
            queryset = queryset.filter(ward__municipality__id=municipality)
        if ward is not None:
            queryset = queryset.filter(ward__code=ward)

        return queryset

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

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer
    filter_class = ResultFilter


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

class ResultSummaryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ResultSummary.objects.all()
    serializer_class = serializers.ResultSummarySerializer
    filter_class = ResultSummaryFilter
