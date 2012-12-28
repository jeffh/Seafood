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
        - postgresql.dev
        - monit
        - java
        - python
        - python.dev
        - python.pip
        - python.virtualenv
        - salt-master.highstate.hourly
        - ksplice
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
