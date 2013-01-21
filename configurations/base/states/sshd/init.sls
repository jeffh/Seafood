{% set sshd = pillar.get('sshd', {}) %}
sshd:
    package:
        - installed
        - name: openssh-server
    service.running:
        - name: ssh
        - watch:
            - package: sshd
            - file: /etc/ssh/sshd_config

'/etc/ssh/sshd_config':
    file.managed:
        - source: salt://sshd/sshd_config
        - mode: 644
        - template: jinja
        - require:
            - package: sshd
        - defaults:
            port: {{ sshd.get('port', 22) }}
            root_can_login: {{ sshd.get('root_can_login', True) }}
            allow_password_auth: {{ sshd.get('allow_password_auth', True) }}

'/etc/monit/conf.d/sshd.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://sshd/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            service_name: {{ pillar['packages'].get('sshd', {}).get('service', 'ssh') }}
            port: {{ sshd.get('port', 22) }}
            pidfile: {{ sshd.get('pidfile', '/var/run/sshd.pid') }}
        - require:
            - package: sshd
            - file: /etc/ssh/sshd_config