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
        - yacs.users
        - yacs.passwords
    'G@roles:yacs and G@roles:webproxy':
        - match: compound
        - yacs.passwords
        - yacs.upstream
    'os:(Ubuntu|Debian)':
        - match: grain_pcre
        - base.ksplice
