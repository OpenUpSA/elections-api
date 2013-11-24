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

    http://iec.code4sa.org/results/?voting_district=10590006
    http://iec.code4sa.org/results/?ward=21001001
    http://iec.code4sa.org/results/?municipality=1
    http://iec.code4sa.org/results/?province=Gauteng

and similarly:
        

    http://iec.code4sa.org/result_summaries/?voting_district=10590006
    http://iec.code4sa.org/result_summaries/?ward=21001001
    http://iec.code4sa.org/result_summaries/?municipality=1
    http://iec.code4sa.org/result_summaries/?province=Western%20Cape

more advanced filtering is also available such as:

    http://iec.code4sa.org/results/?province=Western%20Cape&min_votes=1000

The available filter fields for ```/results``` are:

    votes, max_votes, min_votes,
    party, voting_district, ward, municipality, province

The available filter fields for ```/resultsummaries``` are:

    total_votes, max_total_votes, min_total_votes,
    spoilt_votes, max_spoilt_votes, min_spoilt_votes,
    registered_voters, max_registered_voters, min_registered_voters,
    special_votes, max_special_votes, min_special_votes,
    voter_turnout_perc, max_voter_turnout_perc, min_voter_turnout_perc,
    section_24a_votes, max_section_24a_votes, min_section_24a_votes,
    voting_district, ward, municipality, province
