# this file doesn't include the minion package, since
# they're bootstrapped into the system

'/etc/monit/conf.d/salt-minion.conf':
    file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://salt-master/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            pidfile: /var/run/salt-minion.pid
        - require:
            - pkg: monit
