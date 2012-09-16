from fabric.api import task, env

from bootstrapper.helpers import add_host

############################### HOSTS ###############################
@task
def clear():
    "Removes all added hosts"
    env.hosts = []
    env.passwords = {}

@task
def deploy_host():
    "Adds the deploy_host test machine to hosts"
    add_host('jeff@192.168.1.119', 'p')

@task
def deploy_client():
    "Adds the deploy_client test machine to hosts"
    add_host('jeff@192.168.1.121', 'p')