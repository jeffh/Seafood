base:
    '*':
        - lsb-release
        - upstart
        - sshd
        - users
        - syslog
        - ufw
        - monit
        - salt.minion
        - vim.default
        - curl
    'roles:salt-master':
        - match: grain
        - salt.master
    'roles:gitolite':
        - match: grain
        - gitolite
        - gitolite.post-receive.email
    'roles:golang':
        - match: grain
        - golang
    'roles:jenkins':
        - match: grain
        - repo-keys
        - jenkins
    'G@roles:yacs and G@roles:everything':
        - match: compound
        - nginx
        - memcached
        - memcached.dev
        - coffeescript
        - postgresql
        - postgresql.dev
        - java.core
        - pip
        - virtualenv
        - yacs
    'G@roles:yacs and G@roles:db':
        - match: compound
        - postgresql
    'G@roles:yacs and G@roles:cache':
        - match: compound
        - memcached
    'G@roles:yacs and G@roles:webserver':
        - match: compound
        - nginx
        - memcached
        - memcached.dev
        - coffeescript
        - postgresql.dev
        - java.core
        - pip
        - virtualenv
        - yacs
    'G@roles:yacs and G@roles:webproxy':
        - match: compound
        - nginx
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
