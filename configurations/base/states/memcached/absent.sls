memcached:
    package:
        - purged
    service.dead:
        - enabled: false

memcached_dev:
    package:
        - purged

'/etc/memcached.conf':
    file:
        - absent


'/etc/monit/conf.d/memcached.conf':
    file:
        - absent