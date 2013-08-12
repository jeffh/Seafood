base:
    '*':
        - base.packages
        - caches
    'roles:salt-master':
        - match: grain
        - base.salt-master
