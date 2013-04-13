unattended-upgrades:
    package:
        - installed
        - require:
            - package: lsb-release

'/etc/apt/apt.conf.d':
    file.recurse:
        - source: salt://unattended-upgrades/conf
        - user: root
        - group: root
        - file_mode: 644
        - require:
            - package: unattended-upgrades

