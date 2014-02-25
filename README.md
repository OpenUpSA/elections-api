# Elections API

An API on top of the IEC elections data

## What does this project do

This project implements an HTTP api wrapper around the South African elections data provided
by the Independent Electoral Commission (http://www.elections.org.za/content/Elections/Election-results/).

The goal is to make the election results more accessible by giving developers a simple way of
including this data in their own applications.

## Using the API

Requests to the API should take the following form:

    http://election-results.code4sa.org/<event_type>/<year>/<area>/<id>/?<filter_args>

For example,

    http://election-results.code4sa.org/national/2009/ward/21002004/

retrieves the results for a specific ward in the national elections of 2009.
If the ward's ID is left out

    http://election-results.code4sa.org/national/2009/ward/

then the API will respond with a list of all the known wards, which can be paged through.
But for a quicker way of targeting a specific area's results we can include optional filter arguments. This can
narrow down the search to a province, municipality, or ward of interest, e.g.

    http://election-results.code4sa.org/national/2009/ward/?municipality=EC102

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

### Filter options

Results may be filtered by specifying an ID for any of the area variables. Here are some examples:

    ?province=EASTERN%20CAPE
    ?municipality=EKU
    ?ward=79300006
    ?voting_district=79300006

### Other options

If you just want to retrieve a list of the available areas, without all the overhead of including results, you can
add the following optional query parameter:

    ?include_results=False

TODO: add shapefiles
TODO: filter by latitude & longitude, using a bounding box

## Contributing to the project

This project is open-source, and anyone is welcome to contribute. If you just want to make us aware of a bug / make
a feature request, then please add a new GitHub Issue (if a similar one does not already exist).

If you want to contribute to the code, please fork the repository, make your changes, and create a pull request.

### Local setup

In an new terminal window, create a virtual environment:

    cd <project_dir>
    virtualenv --no-site-packages env
    source env/bin/activate

Install python libraries:

    pip install -r requirements/development.txt

Run Flask dev server:

    python runserver.py

### Deploy instructions

...

### Maintenance

...


