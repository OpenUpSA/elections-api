from fabdefs import *
from fabric.operations import local, run
from fabric.context_managers import lcd
import os

python = "%s/bin/python" % env_dir
pip = "%s/bin/pip" % env_dir

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

def deploy():
    with api.cd(code_dir):
        api.run("git pull origin master")
        api.run("%s install -r %s/requirements/production.txt --quiet" % (pip, code_dir))

        with api.cd(os.path.join(code_dir, project_root)):
            api.run("%s manage.py collectstatic --noinput --settings=settings.production" % python)

        api.sudo("supervisorctl restart iec")
