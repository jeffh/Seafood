base:
    '*':
        - lsb-release
        - upstart
        - sshd
        - users
        - syslog
        - iptables
        - nginx
        - memcached
        - memcached.dev
        - nodejs
        - nodejs.npm
        - nodejs.coffeescript
        - postgresql
        - postgresql.libpq
        - monit
        - java
        - python
        - python.dev
        - python.pip
        - python.virtualenv
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
