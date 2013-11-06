from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from iec import models
import csv
import sys

def clean(val):
    return val.replace(",", "").replace("%", "")

def parse_count(val):
    try:
        return int(clean(val))
    except ValueError:
        return None

def parse_perc(val):
    try:
        return float(clean(val))
    except ValueError:
        return None

class Command(BaseCommand):
    args = "<input file>"
    help = "Load IEC data into database"

    def handle(self, *args, **options):
        row_count = 0
        if len(args) < 1:
            raise CommandError("Expected an input file")
        reader = csv.reader(open(args[0]))
        with transaction.commit_on_success():
            header = reader.next()
            for row in reader:
                if row_count > 5000:
                    print "Commit"
                    transaction.commit()
                    row_count = 0
                row_count += 1


                datum = dict(zip(header, row))
                province = datum["PROVINCE"].capitalize()
                event = datum["ELECTORAL EVENT"].capitalize()
                municipality = datum["MUNICIPALITY"]
                ward = datum["WARD"]
                voting_district = datum["VOTING DISTRICT"]
                party = datum["PARTY NAME"]
                party_votes = parse_count(datum["VALID VOTES"])
                voter_turnout = parse_perc(datum["% VOTER TURNOUT"])
                total_votes = parse_count(datum["TOTAL VOTES CAST"])
                special_votes = parse_count(datum["SPECIAL VOTES"])
                registered_voters = parse_count(datum["REGISTERED VOTERS"])
                section_24a_votes = parse_count(datum["SECTION 24A VOTES"])
                spoilt_votes = parse_count(datum["SPOILT VOTES"])


                province, _ = models.Province.objects.get_or_create(name=province)
                event, _ = models.Event.objects.get_or_create(description=event, type="National")
                municipality, _ = models.Municipality.objects.get_or_create(name=municipality, province=province)
                ward, _ = models.Ward.objects.get_or_create(code=ward, municipality=municipality)
                voting_district, _ = models.VotingDistrict.objects.get_or_create(code=voting_district, ward=ward)
                party, _ = models.Party.objects.get_or_create(name=party)
                rs, created = models.ResultSummary.objects.get_or_create(event=event, voting_district=voting_district)
                if created:
                    rs.voting_district = voting_district
                    rs.total_votes = total_votes
                    rs.special_votes = special_votes
                    rs.registered_voters = registered_voters
                    rs.section_24a_votes = section_24a_votes
                    rs.special_votes = special_votes
                    rs.voter_turnout_perc = voter_turnout
                    rs.spoilt_votes = spoilt_votes
                    rs.save()

                result = models.Result.objects.create(event=event, voting_district=voting_district, party=party) 
                result.votes = party_votes
                result.save()
