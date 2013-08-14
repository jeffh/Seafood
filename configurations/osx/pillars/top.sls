base:
    '*':
        - base.packages
        - caches
        - osx
    'roles:salt-master':
        - match: grain
        - base.salt-master
