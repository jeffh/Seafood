fundamentals:
    file.managed:
        - name: /etc/nginx/sites-enabled/fundamentals
        - source: salt://nginx/sites/django/gunicorn_site.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            name: fundamentals
            listen: '[::]:80 default'
            upstream_servers:
              - host: localhost
                port: 8001
            server_name: localhost
            root: /www/fundamentals/
            static_url: /static/
            static_url: /www/fundamentals/static/
        - require:
            - file: /www/fundamentals/
    environment.set:
        - variables:
            FUNDAMENTALS_ENV: production
    postgres_user.present:
        - password: {{ pillar['passwords']['fundamentals_db'] }}
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
    postgres_database.present:
        - owner: fundamentals
        - runas: postgres
        - require:
            - package: postgresql
            - user: postgresql
            - group: postgresql
            - service: postgresql
            - postgres_user: fundamentals

/www:
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - package: nginx

/www/fundamentals:
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - file: /www

/www/fundamentals/logs:
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - file: /www/fundamentals

/www/fundamentals/static:
    file.symlink:
        - user: www-data
        - group: www-data
        - mode: 755
        - target: /www/fundamentals/django/fundamentals/static/root/
        - require:
            - file: /www/fundamentals