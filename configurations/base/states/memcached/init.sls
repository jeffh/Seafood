{% set mc = pillar.get('memcached', {}) %}
{% set user = mc.get('user', 'memcache') %}
{% set port = mc.get('port', 11211) %}
{% set listen = mc.get('listen', '127.0.0.1') %}
memcached:
    package:
        - installed
    service.running:
        - enabled: true
        - watch:
            - package: memcached
            - file: /etc/memcached.conf
    user.present:
        - name: {{ user }}

'/etc/memcached.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://memcached/files/memcached.conf
        - defaults:
            user: {{ user }}
            port: {{ port }}
            memory: {{ mc.get('memory', 64) }}
            max_value_size: {{ mc.get('max_value_size', '1M') }}
            listen: {{ listen }}
            max_connections: {{ mc.get('max_connections', '1024') }}
            error_on_max: {% if mc.get('error_on_max', False) %}true{% else %}false{% endif %}
            verbose: {% if mc.get('verbose', False) %}true{% else %}false{% endif %}
            logfile: {{ mc.get('logfile', '/var/log/memcached.log') }}
        - require:
            - package: memcached

'/etc/monit/conf.d/memcached.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://memcached/files/monit.conf
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - defaults:
            port: {{ port }}
            listen: {{ listen }}
            pidfile: /var/run/memcached.pid
        - require:
            - package: memcached