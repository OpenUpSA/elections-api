# Code4SA Elections API Installation Guide

## Local setup

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

## Deploy instructions

TODO: add deploy instructions

## Maintenance

To restart the application on a server, use the fabric script:

    fab my_server restart

Logs can be found at:

    * Flask

        /path/to/project_dir/debug.log

    * Nginx:

        /var/log/nginx/error.log
        /var/log/nginx/access.log