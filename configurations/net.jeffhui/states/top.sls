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
        - environment
    'roles:salt-master':
        - match: grain
        - salt.master
    'roles:gitolite':
        - match: grain
        - gitolite
        - gitolite.post-receive.email
    'G@roles:yacs':
        - match: compound
        - yacs
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
