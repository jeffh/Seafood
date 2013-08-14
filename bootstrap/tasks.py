import os
import time

from fabric.api import sudo, task, put, get, env, run, local
from fabric.contrib import files

from bootstrap.config import Settings, Servers
from bootstrap.utils import (
    group, boolean, open_file, get_operating_system, get_config,
    generate_server_names_as_tasks, sync_dir, check_for_sudo,
)

env.passwords = {}
env.servers = {}
env.just_bootstrapped = False
settings = Settings.from_yaml('settings/settings.yml')
servers = Servers.from_yaml('settings/servers.yml')

generate_server_names_as_tasks(servers, globals())


@task
@check_for_sudo
def upload_key(name='~/.ssh/id_rsa.pub'):
    "Uploads your SSH public key to the host to allow ppk-based authentication"
    local_key = os.path.expandvars(os.path.expanduser(name))
    user = env.user
    config = get_config(servers)

    home = sudo('pwd').strip()
    ssh_dir = os.path.join(home, '.ssh')
    sudo('mkdir -p {0!r}; true'.format(ssh_dir))
    sudo('chmod -R 777 {0!r}'.format(ssh_dir))
    with open_file(local_key, config) as handle:
        files.append(os.path.join(ssh_dir, 'authorized_keys'), handle.read())
    sudo('chmod -R 700 {0!r}'.format(ssh_dir))
    sudo('chown -R {0!r} {1!r}'.format(user, ssh_dir))
    sudo('chgrp -R {0!r} {1!r}'.format(group(), ssh_dir))


def bootstrap_salt(master=True, minion=True, syndic=False, upgrade=True, version='stable'):
    """Bootstraps the remote system with salt installed.

    By default the stable version of salt is installed.
    """
    master = boolean(master)
    minion = boolean(minion)
    upgrade = boolean(upgrade)

    config = get_config(servers)
    opsys = get_operating_system(settings.os_detectors)
    boot = settings.bootstrap_for_operating_system(opsys)

    tmp_dir = os.path.join(boot['tmp'], 'seafood-bootstrap')

    sudo('rm -rf {tmp_dir}; true'.format(tmp_dir=tmp_dir))
    sudo('mkdir -p {tmp_dir}'.format(tmp_dir=tmp_dir))
    sudo('chmod -R 777 {tmp_dir}'.format(tmp_dir=tmp_dir))
    bootstrap_script = os.path.join(tmp_dir, 'bootstrap.sh')
    with open_file(boot['script'], config) as handle:
        put(handle, bootstrap_script)
    for filepath in boot['files']:
        with open_file(filepath, config) as handle:
            put(handle, os.path.join(tmp_dir, os.path.basename(filepath)))
    sudo('chmod +x {0}'.format(bootstrap_script))

    args = []
    if master:
        args.append('-M')
    if not minion:
        args.append('-N')
    if syndic:
        args.append('-S')
    if not upgrade:
        args.append('-U')
    if version:
        args.append(version)

    sudo('cd {tmp_dir} && {script} {args}'.format(
        script=bootstrap_script,
        tmp_dir=tmp_dir,
        args=' '.join(map(repr, args)),
    ))


@task
@check_for_sudo
def create_minion_key(hostname):
    """Used on the salt-master to generate ppk for a minion with the given hostname.

    The public and private keys are then downloaded from the master to the local
    keys directory.
    """
    context = dict(
        hostname=hostname,
        key_dir=settings.master_minion_keys_dir,
        user=env.user,
    )
    sudo('salt-key --gen-keys={hostname} --gen-keys-dir={key_dir}'.format(**context))
    sudo('rm -f {hostname}.pem; true'.format(**context))
    sudo('rm -f {hostname}.pub; true'.format(**context))

    sudo('cp -f {key_dir}/{hostname}.pub {key_dir}/{hostname}'.format(**context))
    sudo('chmod 622 {key_dir}/{hostname}'.format(**context))

    sudo('mv {key_dir}/{hostname}.pem {hostname}.pem'.format(**context))
    sudo('mv {key_dir}/{hostname}.pub {hostname}.pub'.format(**context))
    sudo('chown {user} {hostname}.pem'.format(**context))
    sudo('chown {user} {hostname}.pub'.format(**context))
    get('{hostname}.pem'.format(**context), os.path.join('keys', hostname + '.pem'))
    get('{hostname}.pub'.format(**context), os.path.join('keys', hostname + '.pub'))


@task
@check_for_sudo
def upload_keys_to_minion(hostname):
    """Uploads the local keys of the given hostname to the remote host (minion).
    """
    context = dict(
        hostname=hostname,
        key_dir=settings.minion_keys_dir,
        user='root',
        group=group(),
    )

    sudo('rm -f {hostname}.pub; true'.format(**context))
    sudo('rm -f {hostname}.pem; true'.format(**context))
    sudo('rm -f {key_dir}/{hostname}.pub; true'.format(**context))
    sudo('rm -f {key_dir}/{hostname}.pem; true'.format(**context))

    put(os.path.join('keys', hostname + '.pem'))
    put(os.path.join('keys', hostname + '.pub'))

    sudo('mv -f {hostname}.pub {key_dir}/minion.pub'.format(**context))
    sudo('mv -f {hostname}.pem {key_dir}/minion.pem'.format(**context))

    sudo('chown {user} {key_dir}/minion.pub'.format(**context))
    sudo('chown {user} {key_dir}/minion.pem'.format(**context))
    sudo('chgrp {group} {key_dir}/minion.pub'.format(**context))
    sudo('chgrp {group} {key_dir}/minion.pem'.format(**context))
    sudo('chmod 400 {key_dir}/minion.pub'.format(**context))
    sudo('chmod 644 {key_dir}/minion.pem'.format(**context))


@task
@check_for_sudo
def setup_minion(minion_to_master, master_name, bootstrap=True, upgrade=True, restart_service=True):
    """Sets up the minion to point to a given master.

    minion_to_master:
        The address the minion uses to connect to the salt master.
    master_name:
        The fabric hostname task or host string for fabric to connect to the salt master.
    bootstrap:
        Set to False to skip bootstrapping salt. Defaults to True.
    """
    bootstrap = boolean(bootstrap)

    name = hostname()
    local('fab {master_name} create_minion_key:{name}'.format(
        master_name=master_name,
        name=name,
    ))
    upload_keys_to_minion(name)

    if bootstrap:
        bootstrap_salt(master=False, minion=True, upgrade=upgrade)
    server_name = env.servers[env.host_string]['name']
    # upload minion config
    config = get_config(servers)
    minion_config = config.find_file('minion')
    context = dict(
        salt_data_dir=settings.salt_data_dir,
        configs=config.names,
        roles=settings.salt_minion_roles + servers.roles_for_server(server_name),
        master=minion_to_master,
    )
    sudo('mkdir -p {salt_data_dir}; true'.format(**context))
    sudo('mkdir -p /etc/salt/; true'.format(**context))
    files.upload_template(minion_config, os.path.join('/etc/salt/', 'minion'), context=context, use_jinja=True, use_sudo=True)

    if restart_service:
        opsys = get_operating_system(settings.os_detectors)
        bootstrap = settings.bootstrap_for_operating_system(opsys)
        sudo(bootstrap['stop-minion'])
        sudo(bootstrap['start-minion'])


@task
@check_for_sudo
def setup_master(and_minion=True):
    """Sets up the master.

    and_minion:
        Sets up a minion to point to the master (itself). Defaults to True.
    """
    and_minion = boolean(and_minion)

    bootstrap_salt(master=True, minion=and_minion)
    # upload master config
    server_name = env.servers[env.host_string]['name']
    config = servers.configuration_for_server(server_name)
    master_config = config.find_file('master')
    context = dict(
        salt_data_dir=settings.salt_data_dir,
        configs=config.names,
        roles=settings.salt_master_roles + servers.roles_for_server(server_name),
    )
    sudo('mkdir -p {salt_data_dir}; true'.format(**context))
    sudo('mkdir -p /etc/salt/; true'.format(**context))
    files.upload_template(master_config, os.path.join('/etc/salt/', 'master'), context=context, use_jinja=True, use_sudo=True)

    if and_minion:
        setup_minion('127.0.0.1', server_name, bootstrap=False, restart_service=False)
        env.just_bootstrapped = True

    opsys = get_operating_system(settings.os_detectors)
    bootstrap = settings.bootstrap_for_operating_system(opsys)
    sudo(bootstrap['stop-master'])
    sudo(bootstrap['stop-minion'])
    sudo(bootstrap['start-master'])
    sudo(bootstrap['start-minion'])


@task
@check_for_sudo
def hostname(name='', fqdn=False):
    "Gets or sets the machine's hostname"
    fqdn = boolean(fqdn)
    if name:
        previous_host = run('hostname').strip()
        sudo('hostname ' + name)
        sudo('echo {0} > /etc/hostname'.format(name))
        files.sed('/etc/hosts', previous_host, name, use_sudo=True)
    else:
        return sudo('hostname {0}'.format('-f' if fqdn else '')).strip()

@task
@check_for_sudo
def deploy(filter='*', solo=False):
    """Tells master to send pillars and execute salt state files on clients.

    If debug is set to 'yes', runs locally with more debugging information output.
    If upload is set to 'yes', then uploads current salt configurations to the master before deploying.
    """
    solo = boolean(solo)

    if env.just_bootstrapped:
        print "Waiting 30 seconds for minions to connect to master"
        time.sleep(30)

    sudo('mkdir -p {0!r}; true'.format(settings.salt_data_dir))
    config = get_config(servers)

    for path in config.salt_data_dirs:
        src = os.path.join('configurations', path)
        dest = os.path.join(settings.salt_data_dir, path)
        sudo('mkdir -p {0!r}'.format(dest))
        sudo('chown -R {0} {1!r}'.format(env.user, dest))
        sync_dir(src, dest, exclude=['.*'])
        sudo('chown -R root {0!r}'.format(dest))
        sudo('chgrp -R {0} {1!r}'.format(group(), dest))

    sudo('salt --version')
    if solo:
        sudo('salt-call state.highstate -l debug')
    else:
        sudo('salt {0!r} test.version'.format(filter))
        sudo('salt {0!r} saltutil.refresh_pillar'.format(filter))
        sudo('salt {0!r} saltutil.sync_all'.format(filter))
        time.sleep(1)
        sudo('salt {0!r} state.highstate'.format(filter))
