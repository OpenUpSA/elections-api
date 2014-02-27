import json
import csv
from api.models import *
from api import db
db.drop_all()
db.create_all()


def read_data(filename):
    """
    Read election data from CSV file, downloaded at
    http://www.elections.org.za/content/Elections/National-and-provincial-elections-results/
    """

    with open(filename, 'Ur') as f:
        result_list = list(tuple(rec) for rec in csv.reader(f, delimiter=','))

    headings = result_list[0]
    print headings
    result_list = result_list[1::]
    print result_list[333]
    return headings, result_list


def parse_data(result_list, event_desc):
    """

    """

    data_dict = {}

    for row in result_list:

        (
            electoral_event,
            province,
            municipality,
            ward,
            voting_district,
            party_name,
            num_registered,
            turnout_percentage,
            vote_count,
            spoilt_votes,
            total_votes,
            section_24a_votes,
            special_votes
        ) = row

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
    for province in data_dict.keys():
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

    return data_dict


def store_data(data_dict_national, data_dict_provincial, models, year):
    """
    Store given data to the database.
    """

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

    (model_prov, model_munic, model_ward, model_voting_dist) = models

    for province in data_dict_national.keys():
        tmp = model_prov(
            province_id=province_keys[province],
            year=year,
            results_national=json.dumps(data_dict_national[province]['results']),
            results_provincial=json.dumps(data_dict_provincial[province]['results'])
        )
        db.session.add(tmp)
        for municipality in data_dict_national[province]['municipalities'].keys():
            if not "OUT OF COUNTRY" in municipality:
                municipality_code = municipality.split(" ")[0]
                tmp2 = model_munic(
                    province=tmp,
                    municipality_id=municipality_code,
                    year=year,
                    results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['results']),
                    results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['results'])
                )
                db.session.add(tmp2)
                for ward in data_dict_national[province]['municipalities'][municipality]['wards'].keys():
                    if not ward == 'N/A':
                        tmp3 = model_ward(
                            province=tmp,
                            municipality=tmp2,
                            ward_id=int(ward),
                            year=year,
                            results_national=json.dumps(data_dict_national[province]['municipalities'][municipality]['wards'][ward]['results']),
                            results_provincial=json.dumps(data_dict_provincial[province]['municipalities'][municipality]['wards'][ward]['results'])
                        )
                        db.session.add(tmp3)
                        for voting_district in data_dict_national[province]['municipalities'][municipality]['wards'][ward]['voting_districts'].keys():
                            tmp4 = model_voting_dist(
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


if __name__ == "__main__":

    headings, result_list = read_data('election_results/2009 NPE.csv')
    data_dict_national = parse_data(result_list, '22 APR 2009 NATIONAL ELECTION')
    data_dict_provincial = parse_data(result_list, "22 APR 2009 PROVINCIAL ELECTION")

    models = [Province, Municipality, Ward, VotingDistrict]

    # print(json.dumps(data_dict['EASTERN CAPE']['municipalities']['EC101 - CAMDEBOO [GRAAFF-REINET]']['wards']['21001004'], indent=4))

    print "\nNational"
    print(json.dumps(data_dict_national['EASTERN CAPE']['results'], indent=4))
    print "\nProvincial"
    print(json.dumps(data_dict_provincial['EASTERN CAPE']['results'], indent=4))
    store_data(data_dict_national, data_dict_provincial, models, 2009)
    db.session.commit()