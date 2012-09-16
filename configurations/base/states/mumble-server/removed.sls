mumble-server:
    pkg:
        - purged
    service.dead:
        - sig: murmurd
        - enabled: false

'/etc/mumble-server.ini':
    file:
        - absent

'/etc/monit/conf.d/mumble-server.conf':
    file:
        - absent