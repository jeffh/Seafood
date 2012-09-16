===================
Salt Configurations
===================

Here is an example of how to set up a salt configuration system. It includes:

 - Bootstrapping script (via fabric)
 - Customizable configurations for different groups of systems
   (ie - raspberrypi is separated from a different results)

As well as a reference for some moderate tasks:

 - How to use pillars
 - How to write your own modules
 - How to write your own states

This currently only supports Debian / Ubuntu.

------------
Installation
------------

This configuration requires the following dependencies:

- `Python`_
- `pip`_

.. _Python: http://python.org/
.. _pip: http://www.pip-installer.org/en/latest/index.html

Then install all the other dependencies::

    pip install -r requirements.txt

Now you'll need to configure rename some sample files:

 - copy bootstrapper/hosts_sample.py => bootstrapper/hosts.py and edit as appropriate for the hosts to connect.
 - copy configurations/yacs/pillars/passwords_sample.sls => configurations/yacs/pillars/passwords.sls and edit as appropriate. This is only for the yacs configuration (used in "How to use" section).

----------
How to use
----------

Now you can do various `fabric`_ commands to manage basic deployments.

Let's do a basic deploy using `fabric`_. First, we'll set up the salt master::

    fab verbose include:yacs hosts.deploy_host setup_master

.. _fabric: http://docs.fabfile.org/en/1.4.3/index.html

Let's break this command down:

- ``verbose`` is purely optional, it reverts to the default state of fabric to output everything possible about what it's doing. Useful for debugging.
- ``include:yacs`` tells fabric to include the configurations of the given name (yacs in this case). The base configuration is always included by default. Configurations are listed as subdirectories of configurations
- ``hosts.deploy_hosts`` refers to the host to deploy to. They're specified in bootstrapper/hosts.py file. Alternatively, you can use '-H <hostname>' argument instead.
- ``setup_master`` bootstraps salt master and salt minion (which points to itself).

Also, if you want also do an ``apt-get upgrade`` while bootstrapping, you can pass the upgrade=1 argument::

	fab include:yacs hosts.deploy_host setup_master:upgrade=1

It will reboot as necessary after the upgrade.
If you want to see all the detailed output, prefix with the ``verbose`` command::

	fab include:yacs hosts.deploy_host setup_master

All good? Let's deploy a salt minion on another machine::

	fab hosts.deploy_client setup_minion_for_master:hosts.deploy_host,192.168.1.119

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

-----------
Development
-----------

You can use the ``develop`` command before ``setup_master`` and ``setup_minion`` to deploy with the latest git branch (useful for verifying bugfixes)::

    fab include:yacs hosts.deploy_host develop setup_master

Alternatively, you can provide a different public git repository to clone::

    fab include:yacs hosts.deploy_host develop:'git://github.com/jeffh/salt.git' setup_master
