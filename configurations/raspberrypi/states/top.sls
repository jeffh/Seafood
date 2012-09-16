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
        - golang.source.arm5
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
