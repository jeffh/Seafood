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
        # this only works for ubuntu & debian
        sources:
            - elasticsearch: salt://external_files/elasticsearch/0.20.2.deb
    # if not specified explicitly, all packages will use default if available
    #default:
    #    version: latest

# all the repository keys to added before packages are installed
# use the repo-keys state to utilize this.
#
# Currently only apt is supported.
repo-keys:
    # absolute path where keys are stored
    cache-dir: /opt/salt/repo_keys_cache
    # all the keys to add
    add-keys:
        # it uses the 'id' key to verify if the gpg has already been added
        # and the 'source' key is the remote key to download with
        # a hash check if necessary
        jenkins-ci.org.key:
            id: D50582E6
            source: salt://external_files/jenkins/jenkins-ci.org.key
    # likewise, it's possible to remove existing keys.
    # they only need an id and name
    #remove-keys:
    #   jenkins-ci.org.key:
    #       id: D50582E6
