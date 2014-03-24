# Code4SA Elections API Developers Guide

## Using the API

Requests to the API should take the following form:

    http://iec-v2.code4sa.org/<event_type>/<year>/<area>/<id>/?<filter_args>

For example, http://iec-v2.code4sa.org/national/2009/ward/21002004/
retrieves the results for a specific ward in the national elections of 2009.

If the ward's ID is left out: http://iec-v2.code4sa.org/national/2009/ward/ the API will respond with a list of all the known wards, which can be paged through.

For a quicker way of targeting a specific area's results, an optional filter argument can be included. This can
narrow down the search to a province, municipality, or ward of interest, e.g. http://iec-v2.code4sa.org/national/2009/ward/?municipality=EC102

### Available endpoints

When constructing API calls of the form shown above, the following values can be used:

    event_type:

        * national
        * provincial

    year:

        * 1999
        * 2004
        * 2009

    area:

        * province
        * municipality
        * ward
        * voting_district

Please note that ward-level data is not available for the 1999 & 2004 elections. This is because the data is not
included in the IEC's datasets for those two elections.

### Filter options

With the endpoints given above, you can either access a single object of interest (by specifying an id) or a list
of all available objects (e.g. all the wards in the country). This covers a lot of use cases, but there may
be situations where you may want a more specific list of results. For example, you may want to look at all
of the wards in a given municipality, or all of the municipalities in a given province.

For this purpose, the following filters are included in the API:

    ?province=EASTERN%20CAPE
    ?municipality=EKU
    ?ward=79300006
    ?voting_district=79300006

They allow you to efficiently access the child-records of some specified parent area.

### Other options

TODO: option for retrieving area records without results

TODO: add GeoJSON shapes where available

TODO: filter by latitude & longitude, using a bounding box

## Contributing to the project

This project is open-source, and anyone is welcome to contribute. If you just want to make us aware of a bug / make
a feature request, then please add a new GitHub Issue (if a similar one does not already exist).

If you want to contribute to the code, please fork the repository, make your changes, and create a pull request.