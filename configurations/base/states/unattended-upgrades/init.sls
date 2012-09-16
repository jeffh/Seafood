unattended-upgrades:
    pkg:
        - installed
        - require:
            - pkg: lsb-release

'/etc/apt/apt.conf.d/10periodic':
    file.managed:
        - source: salt://unattended-upgrades/10periodic
        - user: root
        - group: root
        - chmod: 644
        - require:
            - pkg: unattended-upgrades

'/etc/apt/apt.conf.d/50unattended-upgrades':
    file.managed:
        - source: salt://unattended-upgrades/50unattended-upgrades
        - user: root
        - group: root
        - chmod: 644
        - require:
            - pkg: unattended-upgrades
