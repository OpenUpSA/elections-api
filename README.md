# Elections API

An API on top of the IEC elections data

## What does this project do

This project implements an HTTP api wrapper around the South African elections data provided
by the Independent Electoral Commission (http://www.elections.org.za/content/Elections/Election-results/).

The goal is to make the election results more accessible by giving developers a simple way of
including this data in their own applications.

## Using the API

Requests to the API should take the following form:

    http://iec-v2.code4sa.org/<event_type>/<year>/<area>/<id>/?<filter_args>

For example,

    http://iec-v2.code4sa.org/national/2009/ward/21002004/

retrieves the results for a specific ward in the national elections of 2009.
If the ward's ID is left out

    http://iec-v2.code4sa.org/national/2009/ward/

then the API will respond with a list of all the known wards, which can be paged through.
But for a quicker way of targeting a specific area's results, an optional filter argument can be included. This can
narrow down the search to a province, municipality, or ward of interest, e.g.

    http://iec-v2.code4sa.org/national/2009/ward/?municipality=EC102

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

### Local setup

After cloning the project, open a terminal window and navigate to the project folder:

    cd <project_dir>

Now create a virtual environment:

    virtualenv --no-site-packages env
    source env/bin/activate

Install python libraries:

    pip install -r requirements/development.txt

Run Flask dev server:

    python runserver.py

The API should now be running at http://localhost:5000, but it won't have any data to display. To populate
the database, first ensure that you have sqlite3 installed on your system. Then download the raw CSV election
result files, and unzip them in the 'election_results' directory:

    cd election_results
    wget http://www.elections.org.za/content/uploadedfiles/2009%20NPE.zip
    unzip '2009 NPE.zip'
    wget http://www.elections.org.za/content/uploadedfiles/2004%20NPE.zip
    unzip '2004 NPE.zip'
    wget http://www.elections.org.za/content/uploadedfiles/1999%20NPE.zip
    unzip '1999 NPE.zip'

Now, build the database with:

    cd ..
    python rebuild_db.py

### Deploy instructions

TODO: add deploy instructions

### Maintenance

To restart the application on a server, use the fabric script:

    fab my_server restart

Logs can be found at:

    * Flask

        /path/to/project_dir/debug.log

    * Nginx:

        /var/log/nginx/error.log
        /var/log/nginx/access.log
