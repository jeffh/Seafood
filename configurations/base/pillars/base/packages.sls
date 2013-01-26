# this is the command to use when an application wants to restart a service
# (ie - monit configs)
service: '/usr/sbin/service'

packages:
    # the keys here are named after the states that define them
    # the dictionary supports everything that pkg.installed unless
    # 'version: latest' is used, in where anything pkg.latest allows.
    #
    # states have default package names and installs the latest version
    # the first time (uses pkg.installed by default).
    # you can specify specific package names and versions here.
    #
    # In addition, many states support the service key, which represents
    # the service name to manage (via service state and monit)
    nginx:
        name: nginx
        # you can optionally specify a specific version by doing:
        # version: 2.0.1ubuntu
        # or use 'latest' to indicate always the most up-to-date version
    # elastic search is not part of standard package repositories,
    # so we'll provide it with the package
    elasticsearch:
        # these two lines below only work for ubuntu & debian
        sources:
            - elasticsearch: salt://packages/elasticsearch/0.20.2.deb
    