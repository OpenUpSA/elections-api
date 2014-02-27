from api import app, logger, db
from flask import jsonify, request, make_response, render_template, redirect
from models import *
import serializers
import json
import time

HOST = app.config['HOST']

event_types = ["provincial", "national"]
years = [1999, 2004, 2009]
areas = ["province", "municipality", "ward", "voting_district"]


class ApiException(Exception):
    """
    Class for handling all of our expected API errors.
    """

    def __init__(self, status_code, message):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {
            "code": self.status_code,
            "message": self.message
        }
        return rv

@app.errorhandler(ApiException)
def handle_api_exception(error):
    """
    Error handler, used by flask to pass the error on to the user, rather than catching it and throwing a HTTP 500.
    """

    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def validate_event_type(event_type):

    event_type = event_type.lower()
    tmp = ", ".join(event_types)
    if not event_type in event_types:
        raise ApiException(422, "Incorrect event_type specified. Please use one of: " + tmp + ".")
    return event_type


def validate_year(year):

    tmp = ", ".join(str(x) for x in years)
    try:
        year = int(year)
    except ValueError as e:
        raise ApiException(422, "Incorrect year specified. Please use one of: " + tmp + ".")
    if not year in years:
        raise ApiException(422, "Incorrect year specified. Please use one of: " + tmp + ".")
    return year


def validate_area(area):

    area = area.lower()
    tmp = ", ".join(areas)
    if not area in areas:
        raise ApiException(422, "Incorrect area specified. Please use one of: " + tmp + ".")
    return area


@app.route('/')
def index_event_types():
    """
    Landing page. Return links to available event_types.
    """

    out = {}
    for event_type in event_types:
        out[event_type] = HOST + "/" + event_type + "/"
    return jsonify(out)


@app.route('/<event_type>/')
def index_years(event_type):
    """
    Return links to available years.
    """

    event_type = validate_event_type(event_type)
    out = {}
    for year in years:
        out[year] = HOST + "/" + event_type + "/" + str(year) + "/"
    return jsonify(out)


@app.route('/<event_type>/<year>/')
def results_overall(event_type, year):
    """
    Return overall national results, with links to available areas.
    """

    event_type = validate_event_type(event_type)
    year = validate_year(year)
    out = {}
    out['results'] = []  # the overall results
    for area in areas:
        out[area] = HOST + "/" + event_type + "/" + str(year) + "/" + area + "/"
    return jsonify(out)


@app.route('/<event_type>/<year>/<area>/')
@app.route('/<event_type>/<year>/<area>/<area_id>/')
def results_by_area(event_type, year, area, area_id=None):
    """
    Return results for the specified area, with links to available parent areas where applicable.
    """

    # validate endpoints
    event_type = validate_event_type(event_type)
    year = validate_year(year)
    area = validate_area(area)

    # validate query parameters
    filter_area = None
    for tmp_area in reversed(areas):
        if request.args.get(tmp_area):
            filter_area = tmp_area
            filter_id = int(request.args.get(tmp_area))

            # throw an exception, if this is not a viable filter for the specified area
            if areas.index(filter_area) >= areas.index(area):
                raise ApiException(422, "The specified filter parameter cannot be used in this query.")
            break


    models = {
        "province": (Province, Province.province_id),
        "municipality": (Municipality, Municipality.municipality_id),
        "ward": (Ward, Ward.ward_id),
        "voting_district": (VotingDistrict, VotingDistrict.voting_district_id)
    }

    if area_id:
        out = models[area][0].query.filter(models[area][1] == area_id).first().as_dict()
    else:
        items = models[area][0].query.limit(20).all()
        out = []
        for item in items:
            out.append(item.as_dict())
    logger.debug(out)

    return make_response(json.dumps(out))