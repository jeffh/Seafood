import os

from fabric.api import sudo, task, put, get, env, run
from fabric.contrib import files

from bootstrap.config import Settings, Configuration
from bootstrap.utils import (
    group, boolean, open_file, get_operating_system, get_config,
    generate_server_names_as_tasks
)

env.passwords = {}
env.servers = {}
settings = Settings.from_yaml('config.yml')

generate_server_names_as_tasks(settings.servers, globals())

@task
def upload_key(name='~/.ssh/id_rsa.pub'):
    local_key = os.path.expandvars(os.path.expanduser(local_key))
    user = env.user
    config = get_config(settings)

    home = silent_sudo('pwd').strip()
    ssh_dir = os.path.join(home, '.ssh')
    sudo('mkdir -p {0!r}; true'.format(ssh_dir))
    sudo('chmod -R 777 {0!r}'.format(ssh_dir))
    with open_file(local_key, config) as handle:
        files.append(os.path.join(ssh_dir, 'authorized_keys'), handle.read())
    sudo('chmod -R 700 {0!r}'.format(ssh_dir))
    sudo('chown -R {0!r} {1!r}'.format(user, ssh_dir))
    sudo('chgrp -R {0!r} {1!r}'.format(group(), ssh_dir))

def bootstrap_salt(master=True, minion=True, syndic=False, upgrade=True, version='stable'):
    master = boolean(master)
    minion = boolean(minion)
    upgrade = boolean(upgrade)

    config = get_config(settings)
    opsys = get_operating_system(settings.os_detectors)
    boot = settings.bootstrap_for_operating_system(opsys)

    tmp_dir = os.path.join(boot['tmp'], 'seafood-bootstrap')

    sudo('rm -rf {tmp_dir}; true'.format(tmp_dir=tmp_dir))
    sudo('mkdir -p {tmp_dir}'.format(tmp_dir=tmp_dir))
    sudo('chmod -R 777 {tmp_dir}'.format(tmp_dir=tmp_dir))
    bootstrap_script = os.path.join(tmp_dir, 'bootstrap.sh')
    put(open_file(boot['script'], config), bootstrap_script)
    for filepath in boot['files']:
        put(open_file(filepath, config), os.path.join(tmp_dir, os.path.basename(filepath)))
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
def create_minion_key(hostname):
    context = dict(
        hostname=hostname,
        key_dir=settings.master_minion_keys_dir,
        user=env.user,
    )
    sudo('salt-key --gen-keys={hostname} --gen-keys-dir={key_dir}'.format(**context))
    sudo('rm -f {hostname}.pem; true'.format(**context))
    sudo('rm -f {hostname}.pub; true'.format(**context))

    sudo('cp {key_dir}/{hostname}.pub {key_dir}/{hostname}'.format(**context))

    sudo('mv {key_dir}/{hostname}.pem {hostname}.pem'.format(**context))
    sudo('mv {key_dir}/{hostname}.pub {hostname}.pub'.format(**context))
    sudo('chown {user} {hostname}.pem'.format(**context))
    sudo('chown {user} {hostname}.pub'.format(**context))
    get('{hostname}.pem'.format(**context), os.path.join('keys', hostname + '.pem'))
    get('{hostname}.pub'.format(**context), os.path.join('keys', hostname + '.pub'))


@task
def upload_keys_to_minion(hostname):
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

    sudo('mv -f {hostname}.pub {key_dir}/{hostname}.pub'.format(**context))
    sudo('mv -f {hostname}.pem {key_dir}/{hostname}.pem'.format(**context))

    sudo('chown {user} {key_dir}/{hostname}.pub'.format(**context))
    sudo('chown {user} {key_dir}/{hostname}.pem'.format(**context))
    sudo('chgrp {group} {key_dir}/{hostname}.pub'.format(**context))
    sudo('chgrp {group} {key_dir}/{hostname}.pem'.format(**context))
    sudo('chmod 400 {key_dir}/{hostname}.pub'.format(**context))
    sudo('chmod 644 {key_dir}/{hostname}.pem'.format(**context))

@task
def setup_minion(master_address, upgrade=0, no_bootstrap=False):
    upgrade = boolean(upgrade)

    bootstrap_salt(master=False, minion=True, upgrade=upgrade)
    server_name = env.servers[env.host_string]['name']
    # upload minion config
    config = get_config(settings)
    master_config = config.find_file('minion')
    context = dict(
        salt_data_dir=settings.salt_data_dir,
        configs=config.names,
        roles=settings.salt_minion_roles + settings.roles_for_server(server_name),
        master=master_address,
    )
    sudo('mkdir -p {salt_data_dir}; true'.format(**context))
    files.upload_template(master_config, os.path.join(context['salt_data_dir'], 'minion'), context=context, use_jinja=True, use_sudo=True)


@task
def setup_master(and_minion=1, upgrade=0):
    and_minion = boolean(and_minion)
    upgrade = boolean(upgrade)

    bootstrap_salt(master=True, minion=and_minion, upgrade=upgrade)
    # upload master config
    server_name = env.servers[env.host_string]['name']
    config = settings.configuration_for_server(server_name)
    master_config = config.find_file('master')
    context = dict(
        salt_data_dir=settings.salt_data_dir,
        configs=config.names,
        roles=settings.salt_master_roles + settings.roles_for_server(server_name),
    )
    sudo('mkdir -p {salt_data_dir}; true'.format(**context))
    files.upload_template(master_config, os.path.join(context['salt_data_dir'], 'master'), context=context, use_jinja=True, use_sudo=True)

    if and_minion:
        name = hostname()
        create_minion_key(name)
        upload_keys_to_minion(name)
        setup_minion(upgrade=False, no_bootstrap=True)

@task
def hostname(name='', fqdn=False):
    "Gets or sets the machine's hostname"
    if name:
        previous_host = run('hostname').strip()
        sudo('hostname ' + name)
        sudo('echo {0} > /etc/hostname'.format(name))
        files.sed('/etc/hosts', previous_host, name, use_sudo=True)
    else:
        return sudo('hostname {0}'.format('-f' if boolean(fqdn) else '')).strip()
