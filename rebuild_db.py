import json
import csv
from api.models import *
from api import db
db.drop_all()
db.create_all()

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

    return data_dict


def store_data_2009(data_dict_national, data_dict_provincial, year):
    """
    Store given data to the database.
    """

    # country-wide aggregate
    tmp = Country(
        year=year,
        results_national=json.dumps(data_dict_national['country']['results']),
        results_provincial=json.dumps(data_dict_provincial['country']['results'])
    )
    db.session.add(tmp)

    # provincial aggergate
    for province, province_id in province_keys.iteritems():
        tmp = Province(
            province_id=province_id,
            year=year,
            results_national=json.dumps(data_dict_national[province]['results']),
            results_provincial=json.dumps(data_dict_provincial[province]['results'])
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
                    results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['results'])
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
                            results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['wards'][ward]['results'])
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
                                results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['wards'][ward]['voting_districts'][voting_district])
                            )
                            db.session.add(tmp4)
    return


def parse_data_old(result_list, event_desc):
    """

    """

    data_dict = {}

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
                }

    # update parents with child results
    for province in data_dict.keys():
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

    return data_dict


def store_data_old(data_dict_national, data_dict_provincial, models, year):
    """
    Store given data to the database.
    """

    (Province, Municipality, VotingDistrict) = models

    for province, province_id in province_keys.iteritems():
        tmp = Province(
            province_id=province_id,
            year=year,
            results_national=json.dumps(data_dict_national[province]['results']),
            results_provincial=json.dumps(data_dict_provincial[province]['results'])
        )
        db.session.add(tmp)
        for municipality in data_dict_national[province]['municipalities'].keys():
            if municipality != 'NULL' and not "OUT OF COUNTRY" in municipality:
                municipality_code = municipality.split(" ")[0]
                tmp2 = Municipality(
                    province=tmp,
                    municipality_id=municipality_code,
                    year=year,
                    results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['results']),
                    results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['results'])
                )
                db.session.add(tmp2)
                for voting_district in data_dict_national[province]['municipalities'][municipality]['voting_districts'].keys():
                    tmp4 = VotingDistrict(
                        province=tmp,
                        municipality=tmp2,
                        voting_district_id=int(voting_district),
                        year=year,
                        results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['voting_districts'][voting_district]),
                        results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['voting_districts'][voting_district])
                    )
                    db.session.add(tmp4)
    return


if __name__ == "__main__":

    # 2009
    # --------------------------------------------------------------------------
    headings, result_list = read_data('election_results/2009 NPE.csv')
    data_dict_national = parse_data_2009(result_list, '22 APR 2009 NATIONAL ELECTION')
    data_dict_provincial = parse_data_2009(result_list, "22 APR 2009 PROVINCIAL ELECTION")

    print "\nNational 2009"
    print(json.dumps(data_dict_national['EASTERN CAPE']['results'], indent=4))
    print "\nProvincial 2009"
    print(json.dumps(data_dict_provincial['EASTERN CAPE']['results'], indent=4))
    store_data_2009(data_dict_national, data_dict_provincial, 2009)
    db.session.commit()

    #
    # # 2004
    # # --------------------------------------------------------------------------
    # headings, result_list = read_data('election_results/2004 NPE.csv')
    # data_dict_national = parse_data_old(result_list, '14 APR 2004 NATIONAL ELECTION')
    # data_dict_provincial = parse_data_old(result_list, "14 APR 2004 PROVINCIAL ELECTION")
    #
    # models = [Province, Municipality, VotingDistrict]
    #
    # print "\nNational 2004"
    # print(json.dumps(data_dict_national['EASTERN CAPE']['results'], indent=4))
    # print "\nProvincial 2004"
    # print(json.dumps(data_dict_provincial['EASTERN CAPE']['results'], indent=4))
    # store_data_old(data_dict_national, data_dict_provincial, models, 2004)
    # db.session.commit()
    #
    #
    # # 1999
    # # --------------------------------------------------------------------------
    # headings, result_list = read_data('election_results/1999 NPE.csv')
    # data_dict_national = parse_data_old(result_list, 'NATIONAL ELECTIONS 1999')
    # data_dict_provincial = parse_data_old(result_list, "PROVINCIAL ELECTIONS 1999")
    #
    # models = [Province, Municipality, VotingDistrict]
    #
    # print "\nNational 1999"
    # print(json.dumps(data_dict_national['EASTERN CAPE']['results'], indent=4))
    # print "\nProvincial 1999"
    # print(json.dumps(data_dict_provincial['EASTERN CAPE']['results'], indent=4))
    # store_data_old(data_dict_national, data_dict_provincial, models, 1999)
    # db.session.commit()