# Code4SA Elections API

The Code4SA Elections API provides a machine-readable dataset sourced from the Electoral Commission of South Africa. It allows you to build a news application, a web page, or any other type of software (or hardware, if you're so inclined) that needs elections data.

This page will discuss what data are available, how you're allowed to use our API, and show some examples of this API being used in the wild. It does not go into the technical details of how to access the API.

If you are a developer and you'd like to dive into the code, go straight to the [Developers Guide](DEVELOPERS_GUIDE.md) or [Installation documentation](INSTALLATION.md).

The goal is to make the election results more accessible by giving developers a simple way of
including this data in their own applications.

## Data Source

This project implements an HTTP api wrapper around the South African elections data provided
by the Independent Electoral Commission (http://www.elections.org.za/content/Elections/Election-results/).

## Let's get started!

The easiest way to use the API is to use our hosted service. Check out the [Terms of Service](#ToS) and if you're happy that you comply, have a look at our [Developers Guide](DEVELOPERS_GUIDE.md) to plug in to the data. 

## What's available?

The data are broadly divided into provincial and national results for each election year.

### National

The national results are broken down as follows:

- Municipality
- Province
- Voting District
- Ward

All results include the following meta-information for each result:

- Number Registered
- Section 24A Votes
- Special Votes
- Spoilt Votes
- Total Votes

In addition, each result includes a vote count per party of every party represented in the specific area.

### Provincial

Provincial votes follow much the same format as the National votes. The results are broken down as follows:

- Municipality
- Province
- Voting District

All results include the following meta-information for each result:

- Number Registered
- Spoilt Votes
- Total Votes
- Years

The following years are available:

- 1999
- 2004
- 2009

##<a name="ToS"></a> Terms of Service

There's very little restriction on how you can use the API. Whether you use it for good or evil is entirely up to you. We do have some restrictions:

### Attribution

The API service is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/). You must attribute us, preferably with a link to the [Code4SA website](http://www.code4sa.org), and if possible display our [logo](http://www.code4sa.org/img/logo.png).

### Rate Limits

We currently have no rate limits. If, however, you're klapping our servers and we feel that you're not playing nicely, we reserve the right to either rate limit you or just lock you out.

We are considering commercial offerings with higher or unlimited rates. At the moment, everything is free for as much as you can eat, so enjoy it while we still feel benevolent.

## Local Development

After cloning the project, open a terminal window and navigate to the project folder:

    cd <project_dir>

Now create a virtual environment:

    virtualenv --no-site-packages env
    source env/bin/activate

Install python libraries:

    pip install -r requirements.txt

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

# Production Deployment

This runs on Heroku.

You will need:

* a New Relic license key
* a random Flask secret key

    heroku create
    heroku addons:add newrelic:stark
    heroku config:set NEW_RELIC_APP_NAME="Elections API" \
                      NEW_RELIC_LICENSE_KEY=some-license-key \
                      FLASK_ENV=production \
                      FLASK_SECRET_KEY=some-secret-key
    git push heroku master
