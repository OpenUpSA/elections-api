import models
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
import django_filters
import serializers
import filters

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer

class PartyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer

class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Province.objects.all()
    serializer_class = serializers.ProvinceSerializer

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.MunicipalitySerializer
    queryset = models.Municipality.objects.all()
    filter_class = filters.MunicipalityFilter

class WardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ward.objects.all()
    serializer_class = serializers.WardSerializer
    filter_class = filters.WardFilter

class VotingDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.VotingDistrict.objects.all()
    serializer_class = serializers.VotingDistrictSerializer
    filter_class = filters.VotingDistrictFilter

class ResultVotesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.VotingDistrict.objects.all()
    serializer_class = serializers.ResultVotesSerializer
    filter_class = filters.VotingDistrictFilter

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer
    filter_class = filters.ResultFilter

    def get_queryset(self):
        event = self.request.QUERY_PARAMS.get('event', 1)
        queryset = models.Result.objects.filter(event__pk=int(event))
        return queryset

class ResultSummaryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ResultSummary.objects.all()
    serializer_class = serializers.ResultSummarySerializer
    filter_class = filters.ResultSummaryFilter

    def get_queryset(self):
        event = self.request.QUERY_PARAMS.get('event', 1)
        queryset = models.ResultSummary.objects.filter(event__pk=int(event))
        return queryset

