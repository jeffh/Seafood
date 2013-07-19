# this file doesn't include the minion package, since
# they're bootstrapped into the system

'/etc/monit/conf.d/salt-minion.conf':
    file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://saltstack/minion/files/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            service_name: {{ pillar['packages'].get('salt-minion', {}).get('service', 'salt-minion') }}
            pidfile: /var/run/salt-minion.pid
        - require:
            - package: monit
