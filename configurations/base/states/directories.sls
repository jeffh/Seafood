'/usr/local/':
    file.directory:
        - user: {{ pillar['root']['user'] }}
        - group: {{ pillar['root']['group'] }}
        - file_mode: 744
        - dir_mode: 755

'/usr/local/bin/':
    file.directory:
        - user: {{ pillar['root']['user'] }}
        - group: {{ pillar['root']['group'] }}
        - file_mode: 755
        - dir_mode: 755
        - require:
            - file: '/usr/local/'
