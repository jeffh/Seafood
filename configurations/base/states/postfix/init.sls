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
        - require:
            - package: postfix
