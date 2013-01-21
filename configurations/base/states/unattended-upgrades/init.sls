unattended-upgrades:
    package:
        - installed
        - require:
            - package: lsb-release

'/etc/apt/apt.conf.d/10periodic':
    file.managed:
        - source: salt://unattended-upgrades/10periodic
        - user: root
        - group: root
        - chmod: 644
        - require:
            - package: unattended-upgrades

'/etc/apt/apt.conf.d/50unattended-upgrades':
    file.managed:
        - source: salt://unattended-upgrades/50unattended-upgrades
        - user: root
        - group: root
        - chmod: 644
        - require:
            - package: unattended-upgrades
