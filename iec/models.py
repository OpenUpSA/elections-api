from django.db import models

event_types = [("Provincial", "Provincial"), ("National", "National")]

class Event(models.Model):
    type = models.CharField(choices=event_types, max_length=15)
    description = models.CharField(max_length=50)

class Province(models.Model):
    name = models.CharField(max_length=20)

class Municipality(models.Model):
    name = models.CharField(max_length=40)
    province = models.ForeignKey(Province)

class Ward(models.Model):
    code = models.CharField(max_length=10)
    municipality = models.ForeignKey(Municipality)

class VotingDistrict(models.Model):
    code = models.CharField(max_length=10)
    ward = models.ForeignKey(Ward)

class Party(models.Model):
    name = models.CharField(max_length=100)

class ResultSummary(models.Model):
    event = models.ForeignKey(Event)
    voting_district = models.ForeignKey(VotingDistrict)
    registered_voters = models.IntegerField(null=True)
    total_votes = models.IntegerField(null=True)
    spoilt_votes = models.IntegerField(null=True)
    special_votes = models.IntegerField(null=True)
    voter_turnout_perc = models.FloatField(null=True)
    section_24a_votes = models.IntegerField(null=True)

class Result(models.Model):
    event = models.ForeignKey(Event)
    voting_district = models.ForeignKey(VotingDistrict)
    party = models.ForeignKey(Party)
    votes = models.IntegerField(null=True)



    
