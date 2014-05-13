import json
import csv
from api.models import *
from api import db
import glob
from itertools import chain
import time
import sqlite3


party_name_overrides = {
    "DEMOCRATIC ALLIANCE/DEMOKRATIESE ALLIANSIE": "DEMOCRATIC ALLIANCE",
    "CONGRESS  OF THE PEOPLE": "CONGRESS OF THE PEOPLE",
    "VRYHEIDSFRONT \\ FREEDOM FRONT": "FREEDOM FRONT",
    "CAPE PARTY/ KAAPSE PARTY": "CAPE PARTY",
    }


province_keys = {
    "LIMPOPO": "LIM",
    "MPUMALANGA": "MP",
    "NORTH WEST": "NW",
    "GAUTENG": "GT",
    "KWAZULU-NATAL": "KZN",
    "EASTERN CAPE": "EC",
    "FREE STATE": "FS",
    "NORTHERN CAPE": "NC",
    "WESTERN CAPE": "WC",
    }

def flatten_dict_values(dictionary):
    return chain.from_iterable(dictionary.values())

def encode(str_in):

    try:
        out = unicode(str_in)
    except UnicodeDecodeError as e:
        clean = ""
        for c in str_in:
            try:
                tmp_char = unicode(c)
                clean += c
            except UnicodeDecodeError as e:
                clean += unichr(ord(c))
        out = clean
    return out

def clear_dbs():
    db.drop_all()
    db.create_all()

def read_data(filename):
    """
    Read election data from CSV file, downloaded at
    http://www.elections.org.za/content/Elections/National-and-provincial-elections-results/
    """

    with open(filename, 'Ur') as f:
        result_list = list(tuple(rec) for rec in csv.reader(f, delimiter=','))

    tmp = result_list[0]
    headings = []
    for i in range(len(tmp)):
        headings.append(tmp[i].replace("\n", " ").replace("  ", " ").strip())
    print headings
    result_list = result_list[1::]
    print result_list[333]
    # convert rows from lists to dicts
    tmp = []
    for row in result_list:
        row_dict = {}
        for i in range(len(row)):
            col = row[i]
            row_dict[headings[i]] = encode(col.strip())
        if not row_dict['PARTY NAME'] == 'NULL':
            tmp.append(row_dict)
    result_list = tmp
    return headings, result_list


def parse_data_2009(result_list, event_desc):
    """

    """

    data_dict = {'country': {'results': {'meta': {}, 'vote_count': {}}, 'wards': {}}}

    for row in result_list:

        # read incoming row of data into local variables
        electoral_event = row.get('ELECTORAL EVENT')
        province = row.get('PROVINCE')
        municipality = row.get('MUNICIPALITY')
        ward = row.get('WARD')
        voting_district = row.get('VOTING DISTRICT')
        party_name = row.get('PARTY NAME')
        num_registered = row.get('REGISTERED VOTERS')
        turnout_percentage = row.get('% VOTERTURNOUT')
        vote_count = row.get('VALID VOTES')
        spoilt_votes = row.get('SPOILT VOTES')
        total_votes = row.get('TOTAL VOTES CAST')
        section_24a_votes = row.get('SECTION 24A VOTES')
        special_votes = row.get('SPECIAL VOTES')

        if party_name_overrides.get(party_name):
            party_name = party_name_overrides[party_name]

        if num_registered == "N/A":
            num_registered = "0"

        special_votes = int(special_votes.replace(',', ''))
        total_votes = int(total_votes.replace(',', ''))
        spoilt_votes = int(spoilt_votes.replace(',', ''))
        section_24a_votes = int(section_24a_votes.replace(',', ''))
        num_registered = int(num_registered.replace(',', ''))

        if electoral_event == event_desc:
            if not data_dict.get(province):
                data_dict[province] = {'results': {'meta': {}, 'vote_count': {}}, 'municipalities': {}}
            if not data_dict[province]['municipalities'].get(municipality):
                data_dict[province]['municipalities'][municipality] = {'results': {'meta': {}, 'vote_count': {}}, 'wards': {}}
            if not data_dict[province]['municipalities'][municipality]['wards'].get(ward):
                data_dict[province]['municipalities'][municipality]['wards'][ward] = {'results': {'meta': {}, 'vote_count': {}}, 'voting_districts': {}}
            if not data_dict[province]['municipalities'][municipality]['wards'][ward]['voting_districts'].get(voting_district):
                data_dict[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district] = {'meta':{}, 'vote_count': {}}
            # save vote count
            data_dict[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district]['vote_count'][party_name] = int(vote_count.replace(',', ''))
            # save meta data
            data_dict[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district]['meta'] = {
                'special_votes': special_votes,
                'total_votes': total_votes,
                'spoilt_votes': spoilt_votes,
                'section_24a_votes': section_24a_votes,
                'num_registered': num_registered,
                'vote_complete': 100,
                }

    # update parents with child results
    for province, province_id in province_keys.iteritems():
        for municipality in data_dict[province]['municipalities'].keys():
            for ward in data_dict[province]['municipalities'][municipality]['wards'].keys():
                for voting_district in data_dict[province]['municipalities'][municipality]['wards'][ward]['voting_districts'].keys():
                    # update ward results from voting district data
                    results = data_dict[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district]
                    counts = data_dict[province]['municipalities'][municipality]['wards'][ward]['results']['vote_count']
                    meta = data_dict[province]['municipalities'][municipality]['wards'][ward]['results']['meta']
                    for party_name, vote_count in results['vote_count'].iteritems():
                        if not counts.get(party_name):
                            counts[party_name] = 0
                        counts[party_name] += vote_count
                    for key, val in results['meta'].iteritems():
                        if not meta.get(key):
                            meta[key] = 0
                        meta[key] += val
                    meta['vote_complete'] = 100
                # update municipality results from ward data
                results = data_dict[province]['municipalities'][municipality]['wards'][ward]['results']
                counts = data_dict[province]['municipalities'][municipality]['results']['vote_count']
                meta = data_dict[province]['municipalities'][municipality]['results']['meta']
                for party_name, vote_count in results['vote_count'].iteritems():
                    if not counts.get(party_name):
                        counts[party_name] = 0
                    counts[party_name] += vote_count
                for key, val in results['meta'].iteritems():
                    if not meta.get(key):
                        meta[key] = 0
                    meta[key] += val
                meta['vote_complete'] = 100
            # update province results from municipality data
            results = data_dict[province]['municipalities'][municipality]['results']
            counts = data_dict[province]['results']['vote_count']
            meta = data_dict[province]['results']['meta']
            for party_name, vote_count in results['vote_count'].iteritems():
                if not counts.get(party_name):
                    counts[party_name] = 0
                counts[party_name] += vote_count
            for key, val in results['meta'].iteritems():
                if not meta.get(key):
                    meta[key] = 0
                meta[key] += val
            meta['vote_complete'] = 100
        # update country-wide results from province data
        results = data_dict[province]['results']
        counts = data_dict['country']['results']['vote_count']
        meta = data_dict['country']['results']['meta']
        for party_name, vote_count in results['vote_count'].iteritems():
            if not counts.get(party_name):
                counts[party_name] = 0
            counts[party_name] += vote_count
        for key, val in results['meta'].iteritems():
            if not meta.get(key):
                meta[key] = 0
            meta[key] += val
        meta['vote_complete'] = 100

    return data_dict


def store_data_2009(data_dict_national, data_dict_provincial, year):
    """
    Store given data to the database.
    """

    # country-wide aggregate
    tmp = Country(
        year=year,
        results_national=json.dumps(data_dict_national['country']['results']),
        results_provincial=json.dumps(data_dict_provincial['country']['results']),
    )
    db.session.add(tmp)

    # provincial aggregate
    for province, province_id in province_keys.iteritems():
        tmp = Province(
            province_id=province_id,
            year=year,
            results_national=json.dumps(data_dict_national[province]['results']),
            results_provincial=json.dumps(data_dict_provincial[province]['results']),
        )
        db.session.add(tmp)
        # municipal aggregate
        for municipality in data_dict_national[province]['municipalities'].keys():
            if not "OUT OF COUNTRY" in municipality:
                municipality_code = municipality.split(" ")[0]
                tmp2 = Municipality(
                    province=tmp,
                    municipality_id=municipality_code,
                    year=year,
                    results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['results']),
                    results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['results']),
                )
                db.session.add(tmp2)
                # ward aggregate
                for ward in data_dict_national[province]['municipalities'][municipality]['wards'].keys():
                    if not ward == 'N/A':
                        tmp3 = Ward(
                            province=tmp,
                            municipality=tmp2,
                            ward_id=int(ward),
                            year=year,
                            results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['wards'][ward]['results']),
                            results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['wards'][ward]['results']),
                        )
                        db.session.add(tmp3)
                        # voting districts
                        for voting_district in data_dict_national[province]['municipalities'][municipality]['wards'][ward]['voting_districts'].keys():
                            tmp4 = VotingDistrict(
                                province=tmp,
                                municipality=tmp2,
                                ward=tmp3,
                                voting_district_id=int(voting_district),
                                year=year,
                                results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district]),
                                results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district]),
                            )
                            db.session.add(tmp4)
    return


def parse_data_old(result_list, event_desc):
    """

    """

    data_dict = {'country': {'results': {'meta': {}, 'vote_count': {}}, 'wards': {}}}

    for row in result_list:

        # read incoming row of data into local variables
        electoral_event = row.get('ELECTORAL EVENT')
        province = row.get('PROVINCE')
        municipality = row.get('MUNICIPALITY')
        voting_district = row.get('VOTING DISTRICT')
        party_name = row.get('PARTY NAME')
        num_registered = row.get('REGISTERED VOTERS')
        turnout_percentage = row.get('% VOTERTURNOUT')
        vote_count = row.get('VALID VOTES')
        spoilt_votes = row.get('SPOILT VOTES')
        total_votes = row.get('TOTAL VOTES CAST')

        if party_name_overrides.get(party_name):
            party_name = party_name_overrides[party_name]

        if num_registered == "N/A":
            num_registered = "0"

        total_votes = int(total_votes.replace(',', ''))
        spoilt_votes = int(spoilt_votes.replace(',', ''))
        num_registered = int(num_registered.replace(',', ''))

        if electoral_event == event_desc:
            if not data_dict.get(province):
                data_dict[province] = {'results': {'meta': {}, 'vote_count': {}}, 'municipalities': {}}
            if not data_dict[province]['municipalities'].get(municipality):
                data_dict[province]['municipalities'][municipality] = {'results': {'meta': {}, 'vote_count': {}}, 'voting_districts': {}}
            if not data_dict[province]['municipalities'][municipality]['voting_districts'].get(voting_district):
                data_dict[province]['municipalities'][municipality]['voting_districts'][voting_district] = {'meta':{}, 'vote_count': {}}
            # save vote count
            data_dict[province]['municipalities'][municipality]['voting_districts'][voting_district]['vote_count'][party_name] = int(vote_count.replace(',', ''))
            # save meta data
            data_dict[province]['municipalities'][municipality]['voting_districts'][voting_district]['meta'] = {
                'total_votes': total_votes,
                'spoilt_votes': spoilt_votes,
                'num_registered': num_registered,
                'vote_complete': 100,
                }

    # update parents with child results
    for province, province_id in province_keys.iteritems():
        for municipality in data_dict[province]['municipalities'].keys():
            for voting_district in data_dict[province]['municipalities'][municipality]['voting_districts'].keys():
                # update municipality results from voting district data
                results = data_dict[province]['municipalities'][municipality]['voting_districts'][voting_district]
                counts = data_dict[province]['municipalities'][municipality]['results']['vote_count']
                meta = data_dict[province]['municipalities'][municipality]['results']['meta']
                for party_name, vote_count in results['vote_count'].iteritems():
                    if not counts.get(party_name):
                        counts[party_name] = 0
                    counts[party_name] += vote_count
                for key, val in results['meta'].iteritems():
                    if not meta.get(key):
                        meta[key] = 0
                    meta[key] += val
                meta['vote_complete'] = 100
            # update province results from municipality data
            results = data_dict[province]['municipalities'][municipality]['results']
            counts = data_dict[province]['results']['vote_count']
            meta = data_dict[province]['results']['meta']
            for party_name, vote_count in results['vote_count'].iteritems():
                if not counts.get(party_name):
                    counts[party_name] = 0
                counts[party_name] += vote_count
            for key, val in results['meta'].iteritems():
                if not meta.get(key):
                    meta[key] = 0
                meta[key] += val
            meta['vote_complete'] = 100
        # update country-wide results from province data
        results = data_dict[province]['results']
        counts = data_dict['country']['results']['vote_count']
        meta = data_dict['country']['results']['meta']
        for party_name, vote_count in results['vote_count'].iteritems():
            if not counts.get(party_name):
                counts[party_name] = 0
            counts[party_name] += vote_count
        for key, val in results['meta'].iteritems():
            if not meta.get(key):
                meta[key] = 0
            meta[key] += val
        meta['vote_complete'] = 100
    return data_dict


def store_data_old(data_dict_national, data_dict_provincial, year):
    """
    Store given data to the database.
    """

    # country-wide aggregate
    tmp = Country(
        year=year,
        results_national=json.dumps(data_dict_national['country']['results']),
        results_provincial=json.dumps(data_dict_provincial['country']['results']),
        # vote_complete = 100
    )
    db.session.add(tmp)

    # provincial aggregate
    for province, province_id in province_keys.iteritems():
        tmp = Province(
            province_id=province_id,
            year=year,
            results_national=json.dumps(data_dict_national[province]['results']),
            results_provincial=json.dumps(data_dict_provincial[province]['results']),
            # vote_complete = 100
        )
        db.session.add(tmp)
        # municipal aggregate
        for municipality in data_dict_national[province]['municipalities'].keys():
            if municipality != 'NULL' and not "OUT OF COUNTRY" in municipality:
                municipality_code = municipality.split(" ")[0]
                tmp2 = Municipality(
                    province=tmp,
                    municipality_id=municipality_code,
                    year=year,
                    results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['results']),
                    results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['results']),
                    # vote_complete = 100
                )
                db.session.add(tmp2)
                # voting districts
                for voting_district in data_dict_national[province]['municipalities'][municipality]['voting_districts'].keys():
                    tmp4 = VotingDistrict(
                        province=tmp,
                        municipality=tmp2,
                        voting_district_id=int(voting_district),
                        year=year,
                        results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['voting_districts'][voting_district]),
                        results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['voting_districts'][voting_district]),
                        # vote_complete = 100
                    )
                    db.session.add(tmp4)
    return

def empty_dict(parties):
    ed = { 'meta': { 'num_registered': 0, 'turnout_percentage': 0, 'vote_count': 0, 'spoilt_votes': 0, 'total_votes': 0, 'section_24a_votes': 0, 'special_votes': 0, 'vote_complete': 0 }, 'vote_count': {} }
    for party in parties:
        ed["vote_count"][party] = 0
    # print ed
    return(ed)

def prep_2014():
   
    # Get party list
    parties = { }
    with open("delims/parties.csv", 'Ur') as f:
        parties_csv = csv.DictReader(f, delimiter=',')
        for party in parties_csv:
            parties[party["province_code"]] = parties.get(party["province_code"], [])
            if (party["name"] not in parties[party["province_code"]]):
                parties[party["province_code"]].append(party["name"])
    country = Country(
        year=2014,
        results_national=json.dumps(empty_dict(parties["ZA"])),
        results_provincial=json.dumps(empty_dict(flatten_dict_values(parties))),
    )
    db.session.add(country)
    db.session.commit()
    with open("delims/province.csv", 'Ur') as f:
        province_csv = csv.DictReader(f, delimiter=',')
        for province in province_csv:
            province_db = Province(
                year=2014,
                results_national=json.dumps(empty_dict(parties["ZA"])),
                results_provincial=json.dumps(empty_dict(parties[province["CODE"]])),
                province_id=province["CODE"],
            )
            db.session.add(province_db)
    db.session.commit()
    province_dict = {}
    with open("delims/municipality.csv", 'Ur') as f:
        municipality_csv = csv.DictReader(f, delimiter=',')
        for municipality in municipality_csv:
            province = Province.query.filter_by(year = "2014", province_id = municipality["PROVINCE"]).first()
            if (province.province_id != "99"):
                # print municipality
                municipality_db = Municipality(
                    year=2014,
                    results_national=json.dumps(empty_dict(parties["ZA"])),
                    results_provincial=json.dumps(empty_dict(parties[province.province_id])),
                    municipality_id=municipality["CAT_B"],
                    province_pk=province.pk
                )
                province_dict[province.pk] = empty_dict(parties[province.province_id])
                db.session.add(municipality_db)
    db.session.commit()
    with open("delims/ward.csv", 'Ur') as f:
        ward_csv = csv.DictReader(f, delimiter=',')
        for ward in ward_csv:
            # print ward
            municipality = Municipality.query.filter_by(year = "2014", municipality_id = ward["CAT_B"]).first()
            ward_db = Ward(
                year=2014,
                results_national=json.dumps(empty_dict(parties["ZA"])),
                results_provincial=json.dumps(province_dict[municipality.province_pk]),
                ward_id=ward["WARD_ID"],
                province_pk=municipality.province_pk,
                municipality_pk=municipality.pk
            )
            db.session.add(ward_db)
    db.session.commit()
    with open("delims/voting_district.csv", 'Ur') as f:
        voting_district_csv = csv.DictReader(f, delimiter=',')
        for voting_district in voting_district_csv:
            ward = Ward.query.filter_by(year = "2014", ward_id = voting_district["FKLWARDID"]).first()
            # print voting_district
            # return 1
            voting_district_db = VotingDistrict(
                year=2014,
                results_national=json.dumps(empty_dict(parties["ZA"])),
                results_provincial=json.dumps(province_dict[ward.province_pk]),
                voting_district_id=voting_district["PKLVDNUMBE"],
                province_pk=ward.province_pk,
                municipality_pk=ward.municipality_pk,
                ward_pk=ward.pk
            )
            db.session.add(voting_district_db)
    db.session.commit()

def test_sqlite3(n=100000, dbname = 'sqlite3.db'):
    conn = init_sqlite3(dbname)
    c = conn.cursor()
    t0 = time.time()
    for i in range(n):
        row = ('NAME ' + str(i),)
        c.execute("INSERT INTO customer (name) VALUES (?)", row)
    conn.commit()
    print "sqlite3: Total time for " + str(n) + " records " + str(time.time() - t0) + " sec"

def import_2014():
    start_time = time.time()
    parties = { }
    results = {}
    presults = {}
    with open("delims/parties.csv", 'Ur') as f:
        parties_csv = csv.DictReader(f, delimiter=',')
        for party in parties_csv:
            parties[party["province_code"]] = parties.get(party["province_code"], [])
            if (party["name"] not in parties[party["province_code"]]):
                parties[party["province_code"]].append(party["name"])
    with open("election_results/2014-results/nat-vds.csv", 'Ur') as f:
        result_list = list(tuple(rec) for rec in csv.reader(f, delimiter=','))
    with open("election_results/2014-results/nat-votes.csv", 'Ur') as f:
        result_votes = list(tuple(rec) for rec in csv.reader(f, delimiter=','))
    with open("election_results/2014-results/prov-vds.csv", 'Ur') as f:
        presult_list = list(tuple(rec) for rec in csv.reader(f, delimiter=','))
    with open("election_results/2014-results/prov-votes.csv", 'Ur') as f:
        presult_votes = list(tuple(rec) for rec in csv.reader(f, delimiter=','))
    print("Opened files, %g seconds" % (time.time() - start_time))
    # print result_votes[0]
    dbvds = db.session.query(VotingDistrict).all()
    vd_prov = {}
    for dbvd in dbvds:
        vd_prov[str(dbvd.voting_district_id)] = db.session.query(Province).filter(Province.pk == dbvd.province_pk).first().province_id
    print("Read all VDs from DB, %g seconds" % (time.time() - start_time))
    # print vd_prov
    for vd in result_list[1:]:
        results[vd[0]] = empty_dict(parties["ZA"])
        results[vd[0]]["meta"]["num_registered"] = vd[1]
        results[vd[0]]["meta"]["vote_count"] = vd[2]
        results[vd[0]]["meta"]["spoilt_votes"] = vd[3]
        results[vd[0]]["meta"]["total_votes"] = vd[4]
        results[vd[0]]["meta"]["vote_complete"] = 100
    print("Compiled national meta, %g seconds" % (time.time() - start_time))
    for vd in presult_list[1:]:
        presults[vd[0]] = empty_dict(parties[vd_prov[vd[0]]])
        presults[vd[0]]["meta"]["num_registered"] = vd[1]
        presults[vd[0]]["meta"]["vote_count"] = vd[2]
        presults[vd[0]]["meta"]["spoilt_votes"] = vd[3]
        presults[vd[0]]["meta"]["total_votes"] = vd[4]
        presults[vd[0]]["meta"]["vote_complete"] = 100
    print("Compiled provincial meta, %g seconds" % (time.time() - start_time))
    queued_keys = []
    for vr in result_votes[1:]:
        results[vr[0]]["vote_count"][vr[1]] = vr[2]
        queued_keys.append(vr[0])
    print("Compiled national results, %g seconds" % (time.time() - start_time))
    for vr in presult_votes[1:]:
        presults[vr[0]]["vote_count"][vr[1]] = vr[2]
        queued_keys.append(vr[0])
    print("Compiled provincial results, %g seconds" % (time.time() - start_time))
    queued_keys = set(queued_keys)
    print("Normalized key list, %g seconds" % (time.time() - start_time))
    print "Queued keys: ", len(queued_keys)
    count = 0
    vdquery = db.session.query(VotingDistrict).filter(VotingDistrict.year == "2014").all()
    conn = sqlite3.connect("instance/tmp.db")
    c = conn.cursor()
    for vd in vdquery:
        if (str(vd.voting_district_id) in queued_keys):
            result = results[str(vd.voting_district_id)]
            presult = presults[str(vd.voting_district_id)]
            c.execute("UPDATE voting_districts SET results_national = ?, results_provincial = ? WHERE pk = ?", (json.dumps(result), json.dumps(presult), vd.pk))
            count = count + 1
        if (count == 1000):
            # db.session.commit()
            conn.commit()
            print("Saved 1000 results, %g seconds" % (time.time() - start_time))
            count=0
            db.session.flush()
    db.session.commit()
    print "Updated ", len(queued_keys), " voting districts"
    print("Finished in %g seconds" % (time.time() - start_time))

def calculate_wards():
    start_time = time.time()
    year = "2014"
    wards = db.session.query(Ward).all()
    conn = sqlite3.connect("instance/tmp.db")
    c = conn.cursor()
    count = 0;
    for ward in wards:
        count = count + 1
        ward_pk = ward.pk
        query = db.session.query(VotingDistrict).filter(VotingDistrict.year == int(year), VotingDistrict.ward_pk == int(ward_pk))
        vds = query.all()
        data_dict = {'meta': {}, 'vote_count': {}}
        data_dict["meta"]["num_registered"] = 0
        data_dict["meta"]["turnout_percentage"] = 0
        data_dict["meta"]["vote_count"] = 0
        data_dict["meta"]["spoilt_votes"] = 0
        data_dict["meta"]["total_votes"] = 0
        data_dict["meta"]["section_24a_votes"] = 0
        data_dict["meta"]["special_votes"] = 0
        data_dict["meta"]["vote_complete"] = 0
        pdata_dict = data_dict
        
        tmp = []
        # print("Calculating ward %s, %g seconds" % (ward_pk, time.time() - start_time))
        for vd in vds:
            data = json.loads(vd.results_national)
            pdata = json.loads(vd.results_provincial)
            for key in data["meta"]:
                data_dict["meta"][key] = int(data_dict["meta"].get(key, 0)) + int(data["meta"][key])
                if (key == "total_votes"):
                    tmp.append(data["meta"][key])
            for key in data["vote_count"]:
                data_dict["vote_count"][key] = int(data_dict["vote_count"].get(key, 0)) + int(data["vote_count"][key])
            for key in pdata["meta"]:
                pdata_dict["meta"][key] = int(pdata_dict["meta"].get(key, 0)) + int(pdata["meta"][key])
                if (key == "total_votes"):
                    tmp.append(pdata["meta"][key])
            for key in pdata["vote_count"]:
                pdata_dict["vote_count"][key] = int(pdata_dict["vote_count"].get(key, 0)) + int(pdata["vote_count"][key])
        
        
        data_dict["meta"]["vote_complete"] = 100
        c.execute("UPDATE wards SET results_national = ?, results_provincial = ? WHERE pk = ?", (json.dumps(data_dict), json.dumps(pdata_dict), ward_pk))
        # db.session.query(Ward).filter(Ward.pk == ward_pk).update({ 'results_national': json.dumps(data_dict), 'results_provincial': json.dumps(pdata_dict) })
        
        # db.session.commit()
        db.session.flush()
        if (count == 10):
            conn.commit()
            print("Computed 10 wards, %g seconds" % (time.time() - start_time))
            count = 0


if __name__ == "__main__":
    
    # clear_dbs()

    # 2009
    # --------------------------------------------------------------------------
    # headings, result_list = read_data('election_results/2009 NPE.csv')
    # data_dict_national = parse_data_2009(result_list, '22 APR 2009 NATIONAL ELECTION')
    # data_dict_provincial = parse_data_2009(result_list, "22 APR 2009 PROVINCIAL ELECTION")

    # print "\nNational 2009"
    
    # print "\nProvincial 2009"
    
    # store_data_2009(data_dict_national, data_dict_provincial, 2009)
    # db.session.commit()


    # # # 2004
    # # # --------------------------------------------------------------------------
    # headings, result_list = read_data('election_results/2004 NPE.csv')
    # data_dict_national = parse_data_old(result_list, '14 APR 2004 NATIONAL ELECTION')
    # data_dict_provincial = parse_data_old(result_list, "14 APR 2004 PROVINCIAL ELECTION")

    # print "\nNational 2004"
    # print(json.dumps(data_dict_national['EASTERN CAPE']['results'], indent=4))
    # print "\nProvincial 2004"
    # print(json.dumps(data_dict_provincial['EASTERN CAPE']['results'], indent=4))
    # store_data_old(data_dict_national, data_dict_provincial, 2004)
    # db.session.commit()


    # # # 1999
    # # # --------------------------------------------------------------------------
    # headings, result_list = read_data('election_results/1999 NPE.csv')
    # data_dict_national = parse_data_old(result_list, 'NATIONAL ELECTIONS 1999')
    # data_dict_provincial = parse_data_old(result_list, "PROVINCIAL ELECTIONS 1999")

    # print "\nNational 1999"
    # print(json.dumps(data_dict_national['EASTERN CAPE']['results'], indent=4))
    # print "\nProvincial 1999"
    # print(json.dumps(data_dict_provincial['EASTERN CAPE']['results'], indent=4))
    # store_data_old(data_dict_national, data_dict_provincial, 1999)
    # db.session.commit()

    # 2014
    # --------------------------------------------------------------------------
    print "\nPrepping for 2014"
    # prep_2014()
    import_2014()
    calculate_wards()
