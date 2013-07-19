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
                max_fails: 2
              {% for server in pillar.get('yacs_upstream', []) %}
              - host: {{ server['host'] }}
                port: {{ server['port'] }}
                max_fails: {{ server.get('max_fails', 1) }}
                weight: {{ server.get('weight', 1) }}
                fail_timeout: {{ server.get('fail_timeout', 10) }}
              {% endfor %}
            server_name: localhost yacs.me
            root: /www/yacs/
            static_url: /static/
            static_root: /www/yacs/static/
        - require:
            - file: /www/yacs
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
