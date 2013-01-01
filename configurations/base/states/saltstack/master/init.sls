# this file doesn't include the master packages, since
# they're bootstrapped into the system

'/etc/monit/conf.d/salt-master.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://salt-master/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            ports:
                - {{ pillar['salt-master']['pub_port'] }}
                - {{ pillar['salt-master']['ret_port'] }}
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
