import os
from fabric.api import (reboot, env, sudo, cd, run, get, put, task)

from bootstrapper.helpers import (silent, silent_remove, remove, chown, chmod, chgrp, git, brew_install)
from bootstrapper.lowlevel.dispatchers import bootstrap
from bootstrapper.lowlevel.utils import upload_key

def install_dmg(local_dmg, resource):
    silent_remove('/tmp/install.dmg')
    put(local_dmg, '/tmp/install.dmg')
    volume = run("hdiutil mount /tmp/install.dmg | grep Volumes | sed 's/.*\/Volumes/\/Volumes/g'")
    sudo('installer -pkg {path!r} -target /'.format(path=os.path.join(volume, resource)))
    run('hdiutil detach {volume!r}'.format(volume=volume))
    silent_remove('/tmp/install.dmg')


@bootstrap.register('darwin')
def bootstrap_osx_homebrew(master, minion, upgrade):
    "Bootstraps OSX to be a salt minion or master using homebrew as the base"
    upload_key()

    # TODO: support env.salt_bleeding
    if not silent('test -e /var/db/receipts/com.apple.pkg.DeveloperToolsCLI.bom'):
        install_dmg('osx/xcode461_cltools_10_86938245a.dmg', 'Command Line Tools (Mountain Lion).mpkg')

    remove('/tmp/homebrew')
    git.using(sudo)('clone', 'https://github.com/mxcl/homebrew.git', '/tmp/homebrew')
    sudo('rsync -axSH /tmp/homebrew/ /usr/local/')
    with cd('/usr/local/'):
        sudo('git clean -fd')
    chmod('775', '/usr/local/')
    chown('root', '/usr/local/')
    chgrp('staff', '/usr/local/')

    brew_install('swig')
    brew_install('zmq')
    brew_install('python')
    run('pip install salt')

    # increase max files limit (os default is 256...)
    # salt-masters need at least 2x the number of clients
    sudo('launchctl limit maxfiles 10000')
    context = dict(python=run('which python'),
                   salt_master=run('which salt-master'),
                   salt_minion=run('which salt-minion'))

    if master:
        config_template_upload('osx/org.saltstack.salt-master.plist', '/Library/LaunchDaemons/org.saltstack.salt-master.plist',
                               context=None, use_sudo=True)
        sudo('launchctl load -w /Library/LaunchDaemons/org.saltstack.salt-master.plist')
    if minion:
        config_template_upload('osx/org.saltstack.salt-minion.plist', '/Library/LaunchDaemons/org.saltstack.salt-minion.plist',
                               context=None, use_sudo=True)
        sudo('launchctl load -w /Library/LaunchDaemons/org.saltstack.salt-minion.plist')

