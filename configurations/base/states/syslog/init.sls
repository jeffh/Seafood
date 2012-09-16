syslog:
    pkg.installed:
        - name: rsyslog
    service.running:
        - name: rsyslog
        - enable: true
        - watch:
            - pkg: syslog
            - file: '/etc/rsyslog.d/*'
    
'/etc/rsyslog.d/':
    file.directory:
        - user: root
        - group: root
        - mode: 644
        - require:
            - pkg: syslog
