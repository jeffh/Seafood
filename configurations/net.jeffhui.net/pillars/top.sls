base:
    '*':
        - base.firewall
        - base.sshd
        - base.users
    'roles:salt-master':
        - match: grain
        - base.salt-master
    'roles:yacs':
        - match: grain
        - yacs.passwords
        - yacs.users
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - base.ksplice