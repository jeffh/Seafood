base:
    '*':
        - base.packages
        - base.sshd
        - linux.postgres
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
        - yacs.environment
        - yacs.users
        - yacs.passwords
        - yacs.upstream
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
