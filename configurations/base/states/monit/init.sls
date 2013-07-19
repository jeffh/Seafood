monit:
    package.installed:
        - order: 1
    service.running:
        - enabled: true
        - order: last
        - watch:
            - package: monit
            - file: /etc/monit/monitrc
            - file: /etc/monit/conf.d/*

'/etc/monit/':
    file.directory:
        - user: root
        - group: root
        - mode: 755
        - order: 1
        - require:
            - package: monit

'/etc/monit/conf.d/':
    file.directory:
        - user: root
        - group: root
        - mode: 755
        - order: 1
        - require:
            - package: monit
            - file: '/etc/monit/'

'/etc/monit/monitrc':
    file.managed:
        - source: salt://monit/files/monitrc
        - user: root
        - group: root
        - mode: 600
        - template: jinja
        - defaults:
            interval: 15 # seconds
            interval_start_delay: '0' # seconds
            logfile: /var/log/monit.log
            idfile: /var/lib/monit/id
            statefile: /var/lib/monit/state
            mmonit: false
            alerts: []
            eventqueue:
                basedir: /var/lib/monit/events
                size: 100
            mail_format:
                from: 'monit@{{ grains["fqdn"] }}'
            webserver:
                port: 2182
                listen: localhost
                allows:
                    - localhost
                    - 'admin:monit'
                    - '@monit'
                    - '@users readonly'
            mail_servers: []
            #mail_servers:
            #   - primary.server port 10243
            #   - localhost
        - require:
            - package: monit
            - file: /etc/monit/
