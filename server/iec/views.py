import models
from rest_framework import viewsets
import serializers

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows an event to be viewed or edited.
    """
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer

class PartyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows party to be viewed or edited.
    """
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer


class ProvinceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a province to be viewed or edited.
    """
    queryset = models.Province.objects.all()
    serializer_class = serializers.ProvinceSerializer

class MunicipalityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a municipality to be viewed or edited.
    """
    serializer_class = serializers.MunicipalitySerializer
    queryset = models.Municipality.objects.all()

    def get_queryset(self):
        queryset = models.Municipality.objects.all()
        province = self.request.QUERY_PARAMS.get('province', None)

        if province is not None:
            queryset = queryset.filter(province__name__iexact=province)
        return queryset

class WardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a ward to be viewed or edited.
    """
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

class VotingDistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a voting district to be viewed or edited.
    """
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

class ResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows result to be viewed or edited.
    """
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer

    def get_queryset(self):
        queryset = models.Result.objects.all()
        voting_district = self.request.QUERY_PARAMS.get('voting_district', None)
        ward = self.request.QUERY_PARAMS.get('ward', None)
        municipality = self.request.QUERY_PARAMS.get('municipality', None)
        province = self.request.QUERY_PARAMS.get('province', None)

        if voting_district is not None:
            queryset = queryset.filter(voting_district__code=voting_district)

        if ward is not None:
            queryset = queryset.filter(voting_district__ward__code=ward)

        if municipality is not None:
            queryset = queryset.filter(voting_district__ward__municipality__pk=municipality)

        if province is not None:
            queryset = queryset.filter(voting_district__ward__municipality__province__pk=province)
        return queryset

class ResultSummaryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a result summary to be viewed or edited.
    """
    queryset = models.ResultSummary.objects.all()
    serializer_class = serializers.ResultSummarySerializer

    def get_queryset(self):
        queryset = models.ResultSummary.objects.all()
        voting_district = self.request.QUERY_PARAMS.get('voting_district', None)
        ward = self.request.QUERY_PARAMS.get('ward', None)
        municipality = self.request.QUERY_PARAMS.get('municipality', None)
        province = self.request.QUERY_PARAMS.get('province', None)

        if voting_district is not None:
            queryset = queryset.filter(voting_district__code=voting_district)

        if ward is not None:
            queryset = queryset.filter(voting_district__ward__code=ward)

        if municipality is not None:
            queryset = queryset.filter(voting_district__ward__municipality__pk=municipality)

        if province is not None:
            queryset = queryset.filter(voting_district__ward__municipality__province__pk=province)
        return queryset
