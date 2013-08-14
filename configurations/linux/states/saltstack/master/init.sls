# this file doesn't include the master packages, since
# they're bootstrapped into the system

'/etc/monit/conf.d/salt-master.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://monit/files/conf.d/basic.conf.template
        - user: root
        - group: root
        - template: jinja
        - defaults:
            name: {{ pillar['packages'].get('salt-master', {}).get('service', 'salt-master') }}
            pidfile: /var/run/salt-master.pid

'/etc/ufw/applications.d/salt.ufw':
    optional_file.managed:
        - onlyif: '[ -e /etc/ufw/applications.d/ ]'
        - source: salt://ufw/application.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            ports: "{{ pillar['salt-master']['pub_port'] }},{{ pillar['salt-master']['ret_port'] }}/tcp"
            title: Salt
            description: Salt is a remote execution and configuration management tool.
