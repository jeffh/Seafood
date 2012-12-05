base:
    '*':
        - sshd
        - users
        - syslog
        - lsb-release
        - nginx
        - monit
        - python
        - python.dev
        - python.pip
        - python.virtualenv
        - mercurial
        - git
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
    master:
        - match: nodegroup
        - salt-master.highstate.hourly
