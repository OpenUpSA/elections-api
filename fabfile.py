from __future__ import with_statement
from fabdefs import *
from fabric.api import *
from contextlib import contextmanager


@contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.activate):
            yield


def restart():

    with settings(warn_only=True):
        sudo('service nginx restart')
        sudo('supervisorctl restart elections-api')
    return


def set_permissions():
    """
     Ensure that www-data has access to the application folder
    """

    sudo('chmod -R 744 ' + env.code_dir)
    sudo('chown -R www-data:www-data ' + env.code_dir)
    return


def download_election_data():

    with cd(env.code_dir):
        with cd('election_results'):
            run('wget http://www.elections.org.za/content/uploadedfiles/2009%20NPE.zip')
            run("unzip '2009 NPE.zip'")
            run('wget http://www.elections.org.za/content/uploadedfiles/2004%20NPE.zip')
            run("unzip '2004 NPE.zip'")
            run('wget http://www.elections.org.za/content/uploadedfiles/1999%20NPE.zip')
            run("unzip '1999 NPE.zip'")
    return


def rebuild_db():

    with cd(env.code_dir):
        with virtualenv():
            sudo('python rebuild_db.py')
    return


def setup():
    """
    Install dependencies and create an application directory.
    """

    with settings(warn_only=True):
        sudo('service nginx stop')

    # install packages
    sudo('apt-get install build-essential python python-dev')
    sudo('apt-get install python-pip supervisor')
    sudo('pip install virtualenv')
    sudo('apt-get install git unzip socket')

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % env.code_dir).failed:
            # create project folder
            sudo('mkdir -p ' + env.code_dir)
            sudo('mkdir -p %s/api' % env.code_dir)
            sudo('mkdir %s/instance' % env.code_dir)
            sudo('mkdir %s/election_results' % env.code_dir)
        if run("test -d %s/env" % env.code_dir).failed:
            # create virtualenv
            sudo('virtualenv --no-site-packages %s/env' % env.code_dir)

    # install the necessary Python packages
    with virtualenv():
        put('requirements/base.txt', '/tmp/base.txt')
        put('requirements/production.txt', '/tmp/production.txt')
        sudo('pip install -r /tmp/production.txt')

    # install nginx
    sudo('apt-get install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    sudo('service nginx start')

    set_permissions()
    return


def configure():
    """
    Upload config files, then restart application.
    """

    with settings(warn_only=True):
        # disable default site
        sudo('rm /etc/nginx/sites-enabled/default')

    # upload nginx server blocks (virtualhost)
    put(env.config_dir + '/nginx.conf', '/tmp/nginx.conf')
    sudo('mv /tmp/nginx.conf %s/nginx_elections-api.conf' % env.code_dir)

    with settings(warn_only=True):
        sudo('ln -s %s/nginx_elections-api.conf /etc/nginx/conf.d/' % env.code_dir)

    # upload supervisor config
    put(env.config_dir + '/supervisor.conf', '/tmp/supervisor.conf')
    sudo('mv /tmp/supervisor.conf /etc/supervisor/conf.d/supervisor_elections-api.conf')
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

    # upload flask config
    put(env.config_dir + '/config.py', '/tmp/config.py')
    sudo('mv /tmp/config.py %s/instance/config.py' % env.code_dir)
    put(env.config_dir + '/config_private.py', '/tmp/config_private.py')
    sudo('mv /tmp/config_private.py %s/instance/config_private.py' % env.code_dir)

    # upload rebuild_db script
    put('rebuild_db.py', '/tmp/rebuild_db.py')
    sudo('mv /tmp/rebuild_db.py %s/rebuild_db.py' % env.code_dir)

    set_permissions()
    restart()
    return


def deploy():
    """
    Upload our package to the server, unzip it, and restart the application.
    """

    # create a tarball of our package
    local('tar -czf api.tar.gz api/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('api.tar.gz', '/tmp/api.tar.gz')

    with settings(warn_only=True):
        sudo('service nginx stop')

    # enter application directory
    with cd(env.code_dir):
        # and unzip new files
        sudo('tar xzf /tmp/api.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /tmp/api.tar.gz')
    local('rm api.tar.gz')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm %s/debug.log*' % env.code_dir)

    set_permissions()
    restart()
    return