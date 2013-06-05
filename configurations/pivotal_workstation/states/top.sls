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
        - pivotal_workstation_base
    'roles:salt-master':
        - match: grain
        - salt.master
    'roles:desktop':
        - match: grain
        - 1password
        - alfred
        - caffeine
        - ccmenu
        - chrome
