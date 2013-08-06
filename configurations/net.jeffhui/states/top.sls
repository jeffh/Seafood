base:
    '*':
        - lsb-release
        - upstart
        - sshd
        - users
        - syslog
        - ufw
        - monit
        - saltstack.minion
        - vim.default
        - curl
        - environment
    'roles:salt-master':
        - match: grain
        - saltstack.master
    'roles:gitolite':
        - match: grain
        - gitolite
        - gitolite.post-receive.email
    'roles:yacs':
        - match: grain
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
