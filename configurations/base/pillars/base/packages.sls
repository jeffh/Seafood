# this is the command to use when an application wants to restart a service
# (ie - monit configs)
service: '/etc/sbin/service'

packages:
    # the keys here are named after the states that define them
    # the dictionary supports everything that pkg.installed unless
    # 'version: latest' is used, in where anything pkg.latest is used.
    #
    # states have default package names and always install the latest version.
    # you can specify specific package names and versions here.
    nginx:
        name: nginx
        # you can optionally specify a specific version by doing:
        # version: 2.0.1ubuntu
        # or use 'latest' to indicate always the most up-to-date version
    salt-master:
        service: salt-master
    salt-minion:
        service: salt-minion