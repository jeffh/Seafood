import os
from StringIO import StringIO
from urlparse import urlparse
from urllib2 import urlopen

from fabric.api import settings, hide, sudo, env, task
import requests

def silent(cmd):
    "Returns the given command without printing stdout or stderr."
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        return sudo(cmd)


def silent_sudo(cmd):
    "Shortcut to silent(cmd, use_sudo=True)"
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        return sudo(cmd)

def boolean(value):
    "Coerces a string value into a boolean"
    return str(value).lower() in (
        'yes', 'y', '1', 'true', 't', 'ok', 'on', 'enabled', 'enable'
    )

def group():
    "Returns the root / admin group. Uses root unless OSX, where the group is staff"
    group = env.user
    is_darwin = not silent_sudo('uname | grep -iq darwin').failed
    if is_darwin:
        group = 'staff'
    return group

def get_config(servers):
    "Gets the Configuration instance for the current server."
    server_name = env.servers[env.host_string]['name']
    return servers.configuration_for_server(server_name)

def get_operating_system(detectors):
    "Returns the operating system type."
    for cmd in detectors:
        command = cmd.keys()[0]
        detect = cmd.values()[0]
        system = sudo(command).strip().lower()
        for name, opsys in detect.items():
            if name in system:
                return opsys
    raise TypeError('Unknown Operating System: ' + system)

def open_file(url, configuration):
    """Returns an open file handle.

    Unlike open, this is aware of various schemes:
        - file (filepath)
        - http (makes a web request)
        - https (makes a web request)
        - salt (looks up the file in the configurations directory

    If no scheme is provided, it is assumed to be a local file path.
    """
    uri = urlparse(url)
    scheme = uri.scheme.lower().strip()
    if scheme in ('file', ''):
        return open(uri.path)
    if scheme == 'salt':
        return open(configuration.find_find(uri.netloc + uri.path))
    if scheme in ('http', 'https'):
        return StringIO(requests.get(url).text)
    raise TypeError('Cannot open url: ' + repr(url))


def generate_server_names_as_tasks(servers, global_vars):
    """Generates tasks for all the servers specified in servers.yml
    """
    def set_server(name, server):
        def fn():
            hostname = server['host']
            env.hosts.append(hostname)
            if 'password' in server:
                env.passwords[hostname] = server['password']
            env.servers[hostname] = server
        fn.__name__ = name
        return fn

    for name, server in servers.items():
        global_vars[name] = task(set_server(name, server))

