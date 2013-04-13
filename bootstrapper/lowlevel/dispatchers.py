from fabric.api import env
from fabric.decorators import hosts

from bootstrapper.helpers import (
    Dispatcher, has, is_platform, apt_remove,
    silent_remove
)
from bootstrapper.lowlevel.utils import set_hostname, reboot_if_required


purge_salt = Dispatcher('purge_salt',
    dispatch=has,
    doc="Removes all salt files from the remote system"
)

bootstrap = Dispatcher('bootstrap',
    dispatch=is_platform,
    doc="Bootstraps the salt minion/master to the given host."
)

@purge_salt.register('apt-get')
def purge_salt_with_apt():
    apt_remove('salt-master', 'salt-minion', 'salt-common')
    silent_remove('/etc/salt', '/opt/salt', '/opt/saltstack', '/var/log/salt')
    silent_remove('/usr/local/bin/salt-*')


@purge_salt.before
def purge_salt_files():
    silent_remove('/etc/salt/')
    silent_remove('/opt/salt/')

@bootstrap.before
def assign_hostname(*args, **kwargs):
    if env.host_string in env.hostnames:
    	hosts(env.host_string)(set_hostname)(env.hostnames[env.host_string])

@bootstrap.after
def perform_reboot(*args, **kwargs):
	reboot_if_required()
