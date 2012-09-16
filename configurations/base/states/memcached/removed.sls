memcached:
    pkg:
        - purged
    service.dead:
        - enabled: false

memcached_dev:
    pkg:
        - purged

'/etc/memcached.conf':
    file:
        - absent


'/etc/monit/conf.d/memcached.conf':
    file:
        - absent