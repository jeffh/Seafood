sshd:
    pkg:
        - installed
        {% if grains['os'] in ('Ubuntu','Debian') %}
        - name: openssh-server
        {% endif %}
    service.running:
        - name: ssh
        - watch:
            - pkg: sshd
            - file: /etc/ssh/sshd_config

'/etc/ssh/sshd_config':
    file.managed:
        - source: salt://sshd/sshd_config
        - mode: 644
        - template: jinja
        - require:
            - pkg: sshd
        - defaults:
            port: {{ pillar['sshd'].get('port', 22) }}
            root_can_login: {{ pillar['sshd'].get('root_can_login', True) }}
            allow_password_auth: {{ pillar['sshd'].get('allow_password_auth', True) }}

'/etc/monit/conf.d/sshd.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://sshd/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            service: ssh
            port: {{ pillar['sshd'].get('port', 22) }}
            pidfile: /var/run/sshd.pid
        - require:
            - pkg: sshd
            - file: /etc/ssh/sshd_config