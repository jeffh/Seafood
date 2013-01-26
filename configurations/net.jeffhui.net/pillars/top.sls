base:
    '*':
        - base.packages
        - base.sshd
        - base.postgres
        - shared.users
        - shared.sshd
    'roles:salt-master':
        - match: grain
        - base.salt-master
    'roles:gitolite':
        - match: grain
        - base.gitolite
    'roles:yacs':
        - match: grain
        - yacs.passwords
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - base.ksplice