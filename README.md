Elections API
=============

An API on top of the IEC elections data

Installation
============

    git clone git@github.com:Code4SA/elections-api.git
    cd elections-api
    fab setup_db
    pip install -r requirements.txt # best to run this in a virtualenv 
    fab setup_db

API
===

You can find a rudimentary API at [http://iec.code4sa.org](http://iec.code4sa.org). You can find example api calls on the home page. In addition, Results and ResultSummaries can be filtered by geographical location e.g.

    http://localhost:8000/results/?voting_district=10590006
    http://localhost:8000/results/?ward=21001001
    http://localhost:8000/results/?municipality=1
    http://localhost:8000/results/?province=1

and similarly
        

    http://localhost:8000/result_summaries/?voting_district=10590006
    http://localhost:8000/result_summaries/?ward=21001001
    http://localhost:8000/result_summaries/?municipality=1
    http://localhost:8000/result_summaries/?province=1

