import models
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework_csv import renderers as r
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

class VotingDistrictVotesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.VotingDistrict.objects.all()
    serializer_class = serializers.VotingDistrictVotesSerializer
    filter_class = filters.VotingDistrictFilter

class WardVotesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ward.objects.all()
    serializer_class = serializers.WardVotesSerializer
    filter_class = filters.WardFilter

class MunicipalityVotesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Municipality.objects.all()
    serializer_class = serializers.MunicipalityVotesSerializer
    filter_class = filters.MunicipalityFilter

class ProvinceVotesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Province.objects.all()
    serializer_class = serializers.ProvinceVotesSerializer

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer
    filter_class = filters.ResultFilter

    def get_queryset(self):
        event = self.request.QUERY_PARAMS.get('event', 1)
        queryset = models.Result.objects.filter(event__pk=int(event))
        return queryset

class FlatResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.FlatResultSerializer
    filter_class = filters.ResultFilter
    renderer_classes =  tuple(api_settings.DEFAULT_RENDERER_CLASSES)  + (serializers.PaginatedCSVRenderer, )

    def get_queryset(self):
        event = self.request.QUERY_PARAMS.get('event', 1)
        queryset = models.Result.objects.filter(event__pk=int(event))
        return queryset

class ResultCSVViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.FlatResultSerializer
    filter_class = filters.ResultFilter
    renderer_classes = (serializers.PaginatedCSVRenderer,)

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

