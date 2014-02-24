from __future__ import with_statement
from fabric.api import *
from contextlib import contextmanager


def common():
    """
    Common environment parameters
    """

    env.activate = 'source %s/env/bin/activate' % env.code_dir
    return

def staging():
    """
    Env parameters for the staging environment.
    """

    env.hosts = ['']
    env.user = 'ubuntu'
    env.envname = 'staging'
    env.key_filename = '~/.ssh/aws_code4sa.pem'
    env.code_dir = '/var/www/elections-api'
    env.config_dir = 'config_staging'
    common()
    print("STAGING ENVIRONMENT\n")
    return


def production():
    """
    Env parameters for the staging environment.
    """

    env.host_string = 'adi@197.221.34.5:2222'
    env.envname = 'production'
    env.code_dir = '/var/www/iec2.code4sa.org'
    env.config_dir = 'config_production'
    common()
    print("PRODUCTION ENVIRONMENT\n")
    return


@contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.activate):
            yield


def setup():

    return


def configure():

    return


def deploy():

    return