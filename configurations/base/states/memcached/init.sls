memcached:
    pkg:
        - installed
    service.running:
        - enabled: true
        - watch:
            - pkg: memcached
            - file: /etc/memcached.conf

'/etc/memcached.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://memcached/memcached.conf
        - defaults:
            user: memcache
            port: 11211
            memory: 64
            max_value_size: 8M
            listen: 127.0.0.1
            max_connections: 1024
            error_on_max: false
            verbose: false
            logfile: /var/log/memcached.log
        - require:
            - pkg: memcached

'/etc/monit/conf.d/memcached.conf':
    optional_file.managed:
        - ifonly: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://memcached/monit.conf
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - defaults:
            port: 11211
            memory: 64
            listen: 127.0.0.1
            pidfile: /var/run/memcached.pid
        - require:
            - pkg: memcached