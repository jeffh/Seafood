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
        - salt.master.highstate-cron
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
    'roles:yacs':
        - match: grain
        - nginx
        - memcached
        - memcached.dev
        - nodejs
        - nodejs.npm
        - nodejs.coffeescript
        - postgresql
        - postgresql.dev
        - java
        - python
        - python.dev
        - python.pip
        - python.virtualenv
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
