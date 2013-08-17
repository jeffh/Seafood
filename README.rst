===================
Salt Configurations
===================

Here is an example of how to set up a salt configuration system. It includes:

- Bootstrapping script (via fabric)
- Customizable configurations for different groups of systems
   (ie - raspberrypis are on a separate network to other systems)

As well as a reference for some moderately difficult tasks:

- How to use pillars
- How to write your own modules
- How to write your own states

This currently only supports Debian / Ubuntu and OSX.

------------
Installation
------------

This configuration requires the following dependencies:

- `Python`_
- `pip`_

.. _Python: http://python.org/
.. _pip: http://www.pip-installer.org/en/latest/index.html

Then install all the other dependencies by doing::

    pip install -r requirements.txt

Now you'll need to configure `_sample` postfixed files which have custom configurations to
equivalent names without the `_sample` postfix if you use them:

- [required] `settings/servers_sample.yml` => `settings/servers.yml` for specifying servers to deploy to.
  Salt-masters require deployment configurations
- `configurations/linux/pillars/linux/http-ping_sample.sls` =>
  `configurations/linux/pillars/linux/http-ping.sls` for configuring
  cron jobs to hit a url (eg - StatHat). 
- `configurations/net.jeffhui/pillars/yacs/passwords_sample.sls` =>
  `configurations/net.jeffhui/pillars/yacs/passwords.sls` for configurating YACS' passwords
- `configurations/net.jeffhui/pillars/yacs/upstream_sample.sls` =>
  `configurations/net.jeffhui/pillars/yacs/upstream.sls` for configuring YACS' nginx
  proxy (if you have multiple app servers)

The sample files can be quickly found using `find`::

    find . -name '*_sample*'

The roles argument are roles you wish the minion to have. 'master' or 'minion' is required for seafood to determine what kind of system the host is.

----------
How to use
----------

Now you can do various `fabric`_ commands to manage basic deployments.

Let's do a basic deploy using `fabric`_. First, we'll set up the salt master::

    fab deploy_host upload_key setup_master

.. _fabric: http://docs.fabfile.org/en/1.4.3/index.html

Let's break this command down:

- ``deploy_host`` refers to the host to deploy to. They're specified in
  `settings/servers.yml` with various options.
- ``upload_key`` uploads your key specified at `~/.ssh/id_rsa.pub`. You can
  optionally specify one by doing: `upload_key:~/.ssh/id_my_other_key.pub`
- ``setup_master`` bootstraps salt master and salt minion (which points to itself) on the target host.

All good? Let's deploy a salt minion on another machine::

	fab deploy_client setup_minion:deploy_host,192.168.1.119

``setup_minion`` requires two arguments:

- The **fabric argument** that refers to the master that our machine can connect to. If you want to use the fabric -H flag, surround it in quotes: ``setup_minion_for_master:'-H 192.168.1.119',192.168.1.119``
- The ip address that the minion will use to connect to the master.

This command actually is several commands:

- ``fab deploy_client hostname`` Returns the hostname of the given host
- ``fab deploy_host generate_minion_key:<hostname>`` Tells the master to generate a public/private key for <hostname> (which is from the previous command)
- ``fab deploy_client minion:192.168.1.119`` Bootstraps the minion which the salt pointed to the given ip address.

Now that both machines are bootstrapped, you can force the salt highstate with a set of configurations::

    fab deploy_host deploy

What does this do?

- Uploads all the pillars and salts to the deploy_host (our master) from the base configuration and yacs configuration using rsync.
- Syncs all custom modules, states, grains using ``salt '*' saltutil.sync_all``
- Runs ``salt '*' state.highstate`` on the master - this propagates all the changes directly to all minions (including itself).

And that's it! You can look around and create your own configurations to tinker
around with salt. Generally, all the shared states go in 'base', where system
group specific configurations are in their own directories.

-----------------
External Packages
-----------------


NOTE: broken for now

Some packages are not in the system repositories. For example, `elasticsearch`.
Using `packages.json`, the packages can be downloaded without being tracked
in the repository. For salt to use these files, they're specified in the
packages.sls pillar.

The packages can be download by running::

    fab download_external_files

Which will download the first package it finds in each group. If you prefer to
download all versions use::

    fab download_external_files:everything=True

---
OSX
---

For OSX, you'll need to download Apple's Command Line Tools DMG in order
to bootstrap a system. It needs to reside in ./osx/xcode_cltools.dmg
