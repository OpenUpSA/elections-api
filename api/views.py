from api import app, logger
from flask import jsonify, request, make_response, render_template, redirect
import models
import serializers
import json
import time

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

    return make_response("OK 1")


@app.route('/<event_type>/')
def index_years(event_type):
    """
    Return links to available years.
    """

    event_type = validate_event_type(event_type)
    return make_response("OK 2")


@app.route('/<event_type>/<year>/')
def results_overall(event_type, year):
    """
    Return overall national results, with links to available areas.
    """

    event_type = validate_event_type(event_type)
    year = validate_year(year)
    return make_response("OK 3")


@app.route('/<event_type>/<year>/<area>/')
def results_by_area(event_type, year, area):
    """
    Return results for the specified area, with links to available parent areas where applicable.
    """

    event_type = validate_event_type(event_type)
    year = validate_year(year)
    area = validate_area(area)
    return make_response("OK 4")