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

You can then add your target hosts to the hosts.py file::

    @task
    def master_host():
        add_host('user@master', 'mypassword', roles=['master'])

    @task
    def minion_host():
        add_host('user@minion', 'mypassword', roles=['minion'])

The roles argument are roles you wish the minion to have. 'master' or 'minion' is required for seafood to determine what kind of system the host is.

----------
How to use
----------

Now you can do various `fabric`_ commands to manage basic deployments.

Let's do a basic deploy using `fabric`_. First, we'll set up the salt master::

    fab include:net.jeffhui.net roles:yacs deploy_host setup_master

.. _fabric: http://docs.fabfile.org/en/1.4.3/index.html

Let's break this command down:

- ``include:net.jeffhui`` tells fabric to include the configurations of the given name (net.jeffhui in this case). The base configuration is always included by default. Configurations are listed as subdirectories of configurations
- ``roles:yacs,everything`` tells fabric what roles this minion (using grains) should have in its configuration, use commas to separate roles.
- ``deploy_host`` refers to the host to deploy to. They're specified in bootstrapper/hosts.py file.
- ``setup_master`` bootstraps salt master and salt minion (which points to itself) on the target host.

Also, if you want to ``apt-get upgrade`` while bootstrapping, you can pass the upgrade=1 argument to setup_master::

	fab include:net.jeffhui.net roles:yacs,evernything deploy_host setup_master:upgrade=1

All good? Let's deploy a salt minion on another machine::

	fab hosts.deploy_client setup_minion:deploy_host,192.168.1.119

``setup_minion_for_master`` requires two arguments:

- The **fabric argument** that refers to the master that our machine can connect to. If you want to use the fabric -H flag, surround it in quotes: ``setup_minion_for_master:'-H 192.168.1.119',192.168.1.119``
- The ip address that the minion will use to connect to the master.

This command actually is several commands:

- ``fab deploy_client hostname`` Returns the hostname of the given host
- ``fab deploy_host lowlevel.generate_minion_key:<hostname>`` Tells the master to generate a public/private key for <hostname> (which is from the previous command)
- ``fab deploy_client minion:192.168.1.119`` Bootstraps the minion which the salt pointed to the given ip address.

Now that both machines are bootstrapped, you can force the salt highstate with a set of configurations::

    fab include:yacs hosts.deploy_host deploy

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

Some packages are not in the system repositories. For example, `elasticsearch`.
Using `packages.json`, the packages can be downloaded without being tracked
in the repository. For salt to use these files, they're specified in the
packages.sls pillar.

The packages can be download by running::

    fab download_external_files

Which will download the first package it finds in each group. If you prefer to
download all versions use::

    fab download_external_files:everything=True

-----------
Development
-----------

You can use the ``develop`` command before ``setup_master`` and ``setup_minion`` to deploy with the latest git branch (useful for verifying bugfixes)::

    fab include:net.jeffhui roles:yacs,everything deploy_host develop setup_master

Alternatively, you can provide a hash of the official git repository to use (defaults to 'develop'):

    fab include:net.jeffhui roles:yacs,everything deploy_host develop:'master' setup_master

Currently, this feature isn't available when deploying to OSX.
