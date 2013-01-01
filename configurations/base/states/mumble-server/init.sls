mumble-server:
    pkg:
        - installed
    service.running:
        - sig: murmurd
        - watch:
            - pkg: mumble-server
            - file: /etc/mumble-server.ini

'/etc/mumble-server.ini':
    file.managed:
        - source: salt://mumble-server/mumble-server.ini
        - user: root
        - group: root
        - template: jinja
        - mode: 640
        - defaults:
            port: 64738
            password:
            welcometext: "<br />Welcome to this server running <b>Murmur</b>.<br />Enjoy your stay!<br />"
            bandwidth: 72000
            maxusers: 100
            logdays: 31
            name:
            requirecert:
            listen:
        - require:
            - pkg: mumble-server

'/etc/monit/conf.d/mumble-server.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://mumble-server/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            listen:
            port: 64738
            pidfile: /var/run/mumble-server
        - require:
            - pkg: mumble-server
            - file: /etc/mumble-server.ini