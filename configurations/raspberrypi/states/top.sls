base:
    '*':
        - sshd
        - users
        - syslog
        - lsb-release
        - monit
        - salt.minion
        - vim.default
    'roles:git':
        - match: grain
        - gitolite
        - gitolite.post-receive.email
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
    'roles:salt-master':
        - match: grain
        - http-ping
        - salt-master
        - salt-master.highstate-cron
