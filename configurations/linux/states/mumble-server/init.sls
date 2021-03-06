mumble-server:
    package:
        - installed
    service.running:
        - sig: murmurd
        - watch:
            - package: mumble-server
            - file: /etc/mumble-server.ini

{% set ms = pillar.get('mumble-server', {}) %}
{% set listen = ms.get('listen', '') %}
{% set port = ms.get('port', 64738) %}
'/etc/mumble-server.ini':
    file.managed:
        - source: salt://mumble-server/files/mumble-server.ini
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - template: jinja
        - mode: 640
        - defaults:
            port: {{ port }}
            password: {{ ms.get('password', '') }}
            welcome_text: "{{ ms.get('welcome_text', "<br />Welcome to this server running <b>Murmur</b>.<br />Enjoy your stay!<br />")}}"
            bandwidth: {{ ms.get('bandwidth', 72000) }}
            maxusers: {{ ms.get('maxusers', 100) }}
            logdays: {{ ms.get('logdays', 31) }}
            name: {{ ms.get('name', '') }}
            requirecert: {{ ms.get('requirecert', 'False') }}
            listen: {{ listen }}
        - require:
            - package: mumble-server

'/etc/monit/conf.d/mumble-server.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://monit/files/conf.d/basic.conf.template
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - template: jinja
        - defaults:
            name: {{ pillar['packages'].get('mumble-server', {}).get('service', 'mumble-server') }}
            pidfile: /var/run/mumble-server
