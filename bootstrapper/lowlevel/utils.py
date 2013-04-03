import os

from fabric.api import reboot, env, settings
from fabric.contrib import files

from bootstrapper.helpers import silent, chmod, mkdir, chown, chgrp, silent_sudo
from bootstrapper.config import CONFIG_DIR, SALT_DIR, master_minions_dir, minion_key_path, group


def config_template_upload(filename, dest, context=None, use_sudo=True):
    context = context or {}
    for config in env.configs:
        filepath = os.path.relpath(os.path.join('configurations', config, filename))
        context['__file__'] = filepath
        if os.path.exists(filepath):
            print 'Use template:', filepath
            files.upload_template(filepath, dest, context=context, use_jinja=True, use_sudo=use_sudo)
            return
        else:
            print '[warn] Template {0} does not exist', repr(filepath)
    raise TypeError('Could not find {0} to upload in any configuration!'.format(repr(filename)))


def salt_config_context(roles=(), **kwargs):
    kwargs.update({
        'saltfiles': SALT_DIR,
        'configs': env.configs,
        'roles': roles,
    })
    return kwargs

def reboot_if_required():
    """Reboots the machine only if the system indicates a restart is required for updates.
    """
    out = silent('[ -f /var/run/reboot-required ]')
    if not out.return_code:
        print "System requires reboot => Rebooting NOW"
        reboot()


def upload_key(local_key='~/.ssh/id_rsa.pub'):
    "Uploads the provided local key to the remote server."
    local_key = os.path.expandvars(os.path.expanduser(local_key))
    user = env.user

    home = silent_sudo('pwd').strip()
    ssh_dir = os.path.join(home, '.ssh')
    with settings(warn_only=True):
        mkdir(ssh_dir)
    chmod(777, ssh_dir)
    with open(local_key) as handle:
        files.append(os.path.join(ssh_dir, 'authorized_keys'), handle.read())
    chmod(700, ssh_dir)
    chown(user, ssh_dir)
    chgrp(group(), ssh_dir)
