===================
Salt Configurations
===================

Here is an example of how to set up a salt configuration system. It includes:

- Bootstrapping script (via fabric)
- Customizable configurations for different groups of systems
   (ie - raspberrypis are on a separate network to other systems)

As well as a reference for some moderate tasks:

- How to use pillars
- How to write your own modules
- How to write your own states

This currently only supports Debian / Ubuntu. (I only have Ubuntu VMs right now...)

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

Now you'll need to configure rename some sample files which have custom configurations:

- copy `bootstrapper/hosts_sample.py` => `bootstrapper/hosts.py` and edit as appropriate for the hosts you want to easily connect to.
- copy `configurations/net.jeffhui.net/pillars/passwords_sample.sls` => `configurations/net.jeffhui.net/pillars/passwords.sls` and edit as appropriate. This is only for the yacs configuration (used in "How to use" section).
- copy `configurations/net.jeffhui.net/states/top_sample.sls` => `configurations/net.jeffhui.net/pillars/top.sls` and edit as appropriate. This is only for the yacs configuration (used in "How to use" section).
- copy `configurations/net.jeffhui.net/pillars/top_sample.sls` => `configurations/net.jeffhui.net/pillars/top.sls` and edit as appropriate. This is only for the yacs configuration (used in "How to use" section).
- copy `configurations/base/pillars/base/ksplice_sample.sls` => `configurations/base/pillars/base/ksplice.sls` and enter your ksplice key. This is used only if you want to have ksplice installed.

The sample files can be quickly found using `find`::

    find . -name '*_sample*'

----------
How to use
----------

Now you can do various `fabric`_ commands to manage basic deployments.

Let's do a basic deploy using `fabric`_. First, we'll set up the salt master::

    fab include:net.jeffhui.net roles:yacs deploy_host setup_master

.. _fabric: http://docs.fabfile.org/en/1.4.3/index.html

Let's break this command down:

- ``include:yacs`` tells fabric to include the configurations of the given name (yacs in this case). The base configuration is always included by default. Configurations are listed as subdirectories of configurations
- ``deploy_host`` refers to the host to deploy to. They're specified in bootstrapper/hosts.py file. Alternatively, you can use '-H <hostname>' argument instead.
- ``setup_master`` bootstraps salt master and salt minion (which points to itself) on the target host.

Also, if you want skip an ``apt-get upgrade`` while bootstrapping, you can pass the upgrade=0 argument to setup_master::

	fab include:net.jeffhui.net roles:yacs deploy_host setup_master:upgrade=0

If you want to see all the detailed output, prefix with the ``verbose`` command::

	fab verbose include:net.jeffhui.net roles:yacs deploy_host setup_master

All good? Let's deploy a salt minion on another machine::

	fab hosts.deploy_client setup_minion:deploy_host,192.168.1.119

``setup_minion_for_master`` requires two arguments:

- The **fabric argument** that refers to the master that our machine can connect to. If you want to use the -H flag, surround it in quotes: ``setup_minion_for_master:'-H 192.168.1.119',192.168.1.119``
- The ip address that minion will use to connect to the master.

This command actually is several commands:

- ``fab hosts.deploy_client hostname`` Returns the hostname of the given host
- ``fab hosts.deploy_host lowlevel.generate_minion_key:<hostname>`` Tells the master to generate a public/private key for <hostname> (which is from the previous command)
- ``fab hosts.deploy_client minion:192.168.1.119`` Bootstraps the minion which the salt pointed to the given ip address.

Now that both machines are bootstrapped, you can force the salt highstate with a set of configurations::

    fab include:yacs hosts.deploy_host deploy

What does this do?

- Uploads all the pillars and salts to the deploy_host (our master) from the base configuration and yacs configuration.
- Runs ``salt '*' state.highstate`` on the master - this propagates all the changes directly to all minions (including itself).

-----------------
External Packages
-----------------

Some packages are not in the system repositories. For example, `elasticsearch`.
Using `packages.json`, the packages can be downloaded without being tracked
in the repository. For salt to use these files, they're specified in the
packages.sls pillar.

-----------
Development
-----------

You can use the ``develop`` command before ``setup_master`` and ``setup_minion`` to deploy with the latest git branch (useful for verifying bugfixes)::

    fab include:yacs hosts.deploy_host develop setup_master

Alternatively, you can provide a different public git repository to clone::

    fab include:yacs hosts.deploy_host develop:'git://github.com/jeffh/salt.git' setup_master
