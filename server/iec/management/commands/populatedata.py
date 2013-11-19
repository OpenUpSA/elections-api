from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from iec import models
import codecs
import unicodecsv as csv
import sys
encoding = "latin1"

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

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.pr_map = {}
        self.ev_map = {}
        self.mun_map = {}
        self.ward_map = {}
        self.vd_map = {}
        self.party_map = {}

    def get_or_create(self, s, mymap, model, **kwargs):
        if s in mymap:
            return mymap[s]
        mymap[s], _ = model.objects.get_or_create(**kwargs)
        return mymap[s]

    def get_province(self, name):
        return self.get_or_create(name, self.pr_map, models.Province, name=name)

    def get_event(self, event):
        return self.get_or_create(event, self.ev_map, models.Event, description=event, type="National")

    def get_municipality(self, munic, province):
        return self.get_or_create(munic, self.mun_map, models.Municipality, name=munic, province=province)

    def get_ward(self, ward, municipality):
        return self.get_or_create(ward, self.ward_map, models.Ward, code=ward, municipality=municipality)

    def get_voting_district(self, vd, ward):
        return self.get_or_create(vd, self.vd_map, models.VotingDistrict, code=vd, ward=ward)

    def get_party(self, party):
        return self.get_or_create(party, self.party_map, models.Party, name=party)

    def _prepopulate(self):
        wards = models.Ward.objects.all()
        self.ward_map = { ward.code : ward for ward in wards }

        vds = models.VotingDistrict.objects.all()
        self.vd_map = { vd.code : vd for vd in vds }

    def setup_foreignkeys(self, fp):
        self._prepopulate()

        reader = csv.reader(fp, encoding=encoding)
        row_count = 0
        with transaction.commit_manually():
            row_count += 1
            header = reader.next()

            for row in reader:
                if row_count % 1000 == 0:
                    sys.stdout.write("\r%d" % row_count)
                    sys.stdout.flush()
                    transaction.commit()
                row_count += 1

                try:
                    datum = dict(zip(header, row))

                    province = self.get_province(datum["PROVINCE"].capitalize())
                    event = self.get_event(datum["ELECTORAL EVENT"].capitalize())
                    municipality = self.get_municipality(datum["MUNICIPALITY"], province)
                    ward = self.get_ward(datum["WARD"], municipality)
                    voting_district = self.get_voting_district(datum["VOTING DISTRICT"], ward)
                    party = self.get_party(datum["PARTY NAME"])
                except Exception, e:
                    import traceback
                    print e
                    traceback.print_exc()
                finally:
                    transaction.commit()
        

    def handle(self, *args, **options):
        row_count = 0
        if len(args) < 1:
            raise CommandError("Expected an input file")
        fp = open(args[0])
        self.setup_foreignkeys(fp)
        fp.seek(0)
        reader = csv.reader(fp, encoding="latin1")
        result_summaries = set()

        print ""
        with transaction.commit_manually():
            header = reader.next()
            for row in reader:
                try:
                    if row_count % 1000 == 0:
                        sys.stdout.write("\r%d" % row_count)
                        sys.stdout.flush()
                        transaction.commit()
                    row_count += 1

                    datum = dict(zip(header, row))

                    event = self.get_event(datum["ELECTORAL EVENT"].capitalize())
                    voting_district = self.get_voting_district(datum["VOTING DISTRICT"], datum["WARD"])
                    party = self.get_party(datum["PARTY NAME"])

                    key = (event, voting_district)
                    if not key in result_summaries:
                        rs = models.ResultSummary.objects.create(
                            event=event, voting_district=voting_district,
                            total_votes=parse_count(datum["TOTAL VOTES CAST"]),
                            special_votes=parse_count(datum["SPECIAL VOTES"]),
                            registered_voters=parse_count(datum["REGISTERED VOTERS"]),
                            section_24a_votes=parse_count(datum["SECTION 24A VOTES"]),
                            voter_turnout_perc=parse_perc(datum["% VOTER TURNOUT"]),
                            spoilt_votes=parse_count(datum["SPOILT VOTES"])
                        )
                        result_summaries.add(key)

                    result = models.Result.objects.create(
                        event=event, voting_district=voting_district, party=party, votes=parse_count(datum["VALID VOTES"])
                    ) 
                except Exception, e:
                    import traceback
                    print e
                    traceback.print_exc()
                finally:
                    transaction.commit()

        print ""
