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
    'roles:salt-master':
        - match: grain
        - salt.master
        - salt.master.highstate-cron
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
        - elasticsearch
        - java
        - python
        - python.dev
        - python.pip
        - python.virtualenv
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
        - ksplice
