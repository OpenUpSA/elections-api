from rest_framework import serializers
from iec import models

class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Party
        fields = ('name', )

class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Event
        fields = ('type', 'description')

class ProvinceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Municipality
        fields = ('name',)

class MunicipalitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Municipality
        fields = ('id', 'name', 'province')

class WardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Ward
        fields = ('code', 'municipality')

class VotingDistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.VotingDistrict
        fields = ('code', 'ward')

class ResultSerializer(serializers.HyperlinkedModelSerializer):
    event = EventSerializer()
    voting_district = VotingDistrictSerializer()
    party = PartySerializer()

    class Meta:
        model = models.Result
        fields = ('event', 'voting_district', 'party', 'votes')

class ResultVoteSerializer(serializers.HyperlinkedModelSerializer):
    party = PartySerializer()
    class Meta:
        model = models.Result
        fields = ('party', 'votes')

class ResultVotesSerializer(serializers.HyperlinkedModelSerializer):
    votes = ResultVoteSerializer(source="result_set")

    class Meta:
        model = models.VotingDistrict


class ResultSummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ResultSummary
