pivotal_workstation_base:
    file.recurse:
        - name: '{{ pillar['caches']['scripts'] }}'
        - source: salt://pivotal_workstation_base/scripts/
        - backup: False
        - user: root
        - group: root
        - dir_mode: 755
        - file_mode: 744
        - makedirs: True
        - recurse:
            - user
            - group
            - mode
        - require:
            - file: '{{ pillar['caches']['packages'] }}'
            - file: '{{ pillar['caches']['tmp'] }}'
        - order: 0

'{{ pillar['caches']['packages'] }}':
    file.directory:
        - user: root
        - group: root
        - dir_mode: 744
        - file_mode: 644
        - makedirs: True
        - recurse:
            - user
            - group
            - mode
        

'{{ pillar['caches']['tmp'] }}':
    file.directory:
        - user: root
        - group: root
        - dir_mode: 777
        - makedirs: True
        - recurse:
            - user
            - group
            - mode

