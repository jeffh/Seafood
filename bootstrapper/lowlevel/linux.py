from fabric.api import (env, sudo)

from bootstrapper.helpers import (remove, chown, chmod, chgrp, git, apt_update, apt_upgrade, has)
from bootstrapper.lowlevel.dispatchers import bootstrap, restart_master, restart_minion
from bootstrapper.lowlevel.utils import reboot_if_required, upload_key


@bootstrap.register('linux')
def bootstrap_linux(master, minion, upgrade):
    "Uses salt bootstrapping to setup the remote server with salt"
    upload_key()
    if upgrade:
        apt_update()
        apt_upgrade()
        reboot_if_required()

    args = []
    if master:
        args.append('-M')
    if not minion:
        args.append('-N')
    if env.salt_bleeding:
        args.append(repr(env.salt_bleeding))

    context = dict(
        sh="sh -s -- {0}".format(' '.join(args)),
        url=env.salt_bootstrap
    )
    if has('wget'):
        sudo("wget -O - {url!r} | {sh}".format(**context))
    elif has('curl'):
        sudo("curl -L {url!r} | {sh}".format(**context))
    elif has('fetch'):
        sudo('fetch -o - {url!r} | {sh}'.format(**context))
    elif has('python'):
        sudo('python -c \'import urllib; print urllib.urlopen("{url}").read()\' | {sh}'.format(**context))
    else:
        raise TypeError('Unable to download and run bootstrap script! ({url!r} | {sh})'.format(**context))

@restart_minion.register('linux')
def minion_service(stop=True, start=True):
    if stop:
        sudo('service salt-minion stop; true')
        time.sleep(1)
        silent_sudo('pkill salt-minion')
        time.sleep(1)
    if start:
        sudo('service salt-minion start')

@restart_master.register('linux')
def restart_master(stop=True, start=True):
    if stop:
        sudo('service salt-master stop; true')
        time.sleep(1)
        silent_sudo('pkill salt-minion')
        time.sleep(1)
    if start:
        sudo('service salt-master start')



