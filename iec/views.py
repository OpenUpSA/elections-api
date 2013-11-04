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
    queryset = models.Municipality.objects.all()
    serializer_class = serializers.MunicipalitySerializer

class WardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a ward to be viewed or edited.
    """
    queryset = models.Ward.objects.all()
    serializer_class = serializers.WardSerializer

class VotingDistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a voting district to be viewed or edited.
    """
    queryset = models.VotingDistrict.objects.all()
    serializer_class = serializers.VotingDistrictSerializer

class ResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows result to be viewed or edited.
    """
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer

class ResultSummaryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a result summary to be viewed or edited.
    """
    queryset = models.ResultSummary.objects.all()
    serializer_class = serializers.ResultSummarySerializer
