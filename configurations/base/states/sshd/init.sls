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
        - source: salt://sshd/files/sshd_config
        - mode: 644
        - template: jinja
        - require:
            - package: sshd
        - defaults:
            port: {{ salt['pillar.get']('sshd:port', 22) }}
            root_can_login: {{ salt['pillar.get']('sshd:root_can_login', True) }}
            allow_password_auth: {{ salt['pillar.get']('sshd:allow_password_auth', False) }}

'/etc/monit/conf.d/sshd.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://sshd/files/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            service_name: {{ salt['pillar.get']('packages:sshd:service', 'ssh') }}
            port: {{ salt['pillar.get']('sshd:port', 22) }}
            pidfile: {{ salt['pillar.get']('sshd:pid_file', '/var/run/sshd.pid') }}
        - require:
            - package: sshd
            - file: /etc/ssh/sshd_config
