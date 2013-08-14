osx_base:
    file.recurse:
        - name: '{{ pillar['caches']['scripts'] }}'
        - source: salt://osx_base/scripts/
        - backup: False
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
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
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - dir_mode: 744
        - file_mode: 644
        - makedirs: True
        - recurse:
            - user
            - group
            - mode

'{{ pillar['caches']['tmp'] }}':
    file.directory:
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - dir_mode: 777
        - makedirs: True
        - recurse:
            - user
            - group
            - mode

'{{ pillar['caches']['hashes'] }}':
    file.directory:
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - dir_mode: 744
        - file_mode: 644
        - makedirs: True
        - recurse:
            - user
            - group
            - mode

