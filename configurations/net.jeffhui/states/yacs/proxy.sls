include:
    - nginx

yacs_proxy:
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
              {% if not pillar.get('yacs_upstream', []) %}[]{% endif %}
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
