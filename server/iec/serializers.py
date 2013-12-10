from rest_framework import serializers
from iec import models

class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Party
        fields = ("name", )

class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Event
        fields = ("type", "description")

class ProvinceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Municipality
        fields = ("name",)

class MunicipalitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Municipality
        fields = ("id", "name", "province")

class WardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Ward
        fields = ("code", "municipality")

class VotingDistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.VotingDistrict
        fields = ("code", "ward")

class ResultSerializer(serializers.HyperlinkedModelSerializer):
    event = EventSerializer()
    voting_district = VotingDistrictSerializer()
    party = PartySerializer()

    class Meta:
        model = models.Result
        fields = ("event", "voting_district", "party", "votes")

class ResultVoteSerializer(serializers.HyperlinkedModelSerializer):
    party = PartySerializer()
    class Meta:
        model = models.Result
        fields = ("party", "votes")

class VotingDistrictVotesSerializer(serializers.HyperlinkedModelSerializer):
    votes = ResultVoteSerializer(source="result_set")

    class Meta:
        model = models.VotingDistrict

from django.db.models import Count, Sum

class WardVoteField(serializers.Field):
    def to_native(self, voting_districts):
        # TODO - need to do this properly
        national_event = 1
        results = models.Result.objects.filter(
            voting_district__in=voting_districts.all(), event=national_event)

        results = results.values("party__name").annotate(num_votes=Sum("votes"))
        
        return [
            { "party" : r["party__name"], "votes" : r["num_votes"]}
            for r in results
        ]

class WardVotesSerializer(serializers.HyperlinkedModelSerializer):
    votes = WardVoteField(source="votingdistrict_set")

    class Meta:
        model = models.Ward
        fields = ("code", "municipality", "votes")

class MunicipalityVoteField(serializers.Field):
    def to_native(self, wards):
        wds = wards\
            .values("votingdistrict__result__party__name")\
            .annotate(num_votes=Sum("votingdistrict__result__votes"))
        
        return [
            { "party" : ward["votingdistrict__result__party__name"], "votes" : ward["num_votes"]}
            for ward in wds
        ]

class MunicipalityVotesSerializer(serializers.HyperlinkedModelSerializer):
    votes = MunicipalityVoteField(source="ward_set")

    class Meta:
        model = models.Municipality
        fields = ("id", "name", "province", "votes")

class ProvinceVoteField(serializers.Field):
    def to_native(self, munics):
        ms = munics\
            .values("ward__votingdistrict__result__party__name")\
            .annotate(num_votes=Sum("ward__votingdistrict__result__votes"))
        
        return [
            {
                "party" : m["ward__votingdistrict__result__party__name"],
                "votes" : m["num_votes"]
            }
            for m in ms
        ]

class ProvinceVotesSerializer(serializers.HyperlinkedModelSerializer):
    votes = ProvinceVoteField(source="municipality_set")

    class Meta:
        model = models.Municipality
        fields = ("id", "name", "votes")

class ResultSummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ResultSummary
