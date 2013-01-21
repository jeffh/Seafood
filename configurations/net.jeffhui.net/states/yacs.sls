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
    file.managed:
        - name: /etc/nginx/sites-enabled/yacs
        - source: salt://nginx/sites/django/gunicorn_site.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            listen: '[::]:80 default'
            app_name: yacs
            upstream_servers:
              - host: localhost
                port: 8000
            server_name: localhost yacs.me
            root: /www/yacs/
            static_url: /static/
            static_root: /www/yacs/static/
        - require:
            - file: /www/yacs
    environment.set:
        - variables:
            YACS_ENV: production
    postgres_user.present:
        - password: {{ pillar['passwords']['yacs_db'] }}
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
    postgres_database.present:
        - owner: yacs
        - runas: postgres
        - require:
            - package: postgresql
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
            - package: nginx

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