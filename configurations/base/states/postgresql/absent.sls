postgresql:
    package:
        - purged
        - require:
            - service: postgresql
    service.dead:
        - enabled: false

{% set version = '9.1' %}

'/etc/postgresql/{{ version }}/':
    file:
        - absent
