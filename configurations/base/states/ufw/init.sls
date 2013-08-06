ufw:
    package:
        - installed
    service.running:
        - watch:
            - package: ufw
            - file: '/etc/ufw/*'
    cmd.run:
        - name: 'ufw enable'
        - onlyif: 'ufw status | grep -E inactive'
        - require:
            - package: ufw
            - cmd: '/etc/ufw/applications.d'

'/etc/ufw/applications.d':
    file.directory:
        - user: root
        - group: root
        - file_mode: 644
        - dir_mode: 755
        - require:
            - package: ufw
    cmd.run:
        - name: "yes | ufw reset && ufw enable && ufw app list | grep '^ .*$' | while read app; do ufw allow \"$app\"; done"
        - unless: "diff <(ufw status | grep -v '(v6)'  | grep ALLOW | sed 's/ *ALLOW.*//g') <(ufw app list | grep '^ ' | sed -e 's/^[ \t]*//g')"
        - shell: /bin/bash
        - require:
            - package: ufw
        - watch:
            - package: *
            - file: '/etc/ufw/applications.d'
