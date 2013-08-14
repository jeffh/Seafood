postfix:
    package:
        - installed
    service.running:
        - watch:
            - package: postfix
            - file: '/etc/postfix/*'

'/etc/postfix':
    file.recurse:
        - source: salt://postfix/files
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - require:
            - package: postfix
