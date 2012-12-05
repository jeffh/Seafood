base:
    '*':
        - lsb-release
        - upstart
        - sshd
        - users
        - syslog
        - iptables
        - nginx
        - monit
        - php.cgi
        - mysql
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - unattended-upgrades
