syslog:
    package.installed:
        - name: rsyslog
    service.running:
        - name: rsyslog
        - enable: true
        - watch:
            - package: syslog
            - file: '/etc/rsyslog.d/*'
    
'/etc/rsyslog.d/':
    file.directory:
        - user: root
        - group: root
        - mode: 644
        - require:
            - package: syslog
