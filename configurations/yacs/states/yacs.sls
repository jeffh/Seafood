include:
    - sshd

extend:
    '/etc/ssh/sshd_config':
        file.managed:
            - context:
                port: 22
                root_can_login: true
                allow_password_auth: true

yacs:
    file.append:
        - name: /etc/environment
        - text: YACS_ENV=production
    postgres_user.present:
        - password: {{ pillar['passwords']['yacs_db'] }}
        - runas: postgres
        - require:
            - pkg: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
    postgres_database.present:
        - owner: yacs
        - runas: postgres
        - require:
            - pkg: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
            - postgres_user: yacs

/www:
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - pkg: nginx

/www/yacs:
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - file: /www

/www/yacs/logs:
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - file: /www/yacs

/www/yacs/static:
    file.symlink:
        - user: www-data
        - group: www-data
        - mode: 755
        - target: /www/yacs/django/yacs/static/root/
        - require:
            - file: /www/yacs