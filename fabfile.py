from fabric.operations import local, run
from fabric.context_managers import lcd
import os

elections_url = "http://www.elections.org.za/content/uploadedfiles/2009%20NPE.zip"
elections_file = "2009 NPE.csv"
os.environ["DJANGO_SETTINGS_MODULE"] = "iec.local"
project_root = "server"

def download_data():
    local("mkdir -p data")

    with lcd('data'):
        local("wget -N '{}'".format(elections_url))
        local("unzip '{}'".format("*.zip"))
        local("sed -e :a -e N -e '1,9 s/\\n/ /' -e ta '{}' > out".format(elections_file))
        local("mv out '{}'".format(elections_file))

def setup_db():
    download_data()
    with lcd(project_root):
        local("python manage.py syncdb")
        local("python manage.py loaddata '../data/{}'".format(elections_file))
