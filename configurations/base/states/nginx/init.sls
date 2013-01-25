nginx:
    package:
        - installed
    service.running:
        - watch:
            - package: nginx
            - file: '/etc/nginx/*'

'/etc/monit/conf.d/nginx.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://nginx/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            service_name: {{ pillar['packages'].get('nginx', {}).get('service', 'nginx') }}
            ports:
                - number: 80
                  ssl: False
            pidfile: /var/run/nginx.pid

'/usr/share/nginx/www/':
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - package: nginx
            
'/etc/nginx/sites-available':
    file:
        - absent
        - require:
            - package: nginx
            
'/etc/nginx/':
    file.directory:
        - user: root
        - group: root
        - file_mode: 755
        - require:
            - package: nginx
            
'/etc/nginx/sites-enabled/':
    file.directory:
        - user: root
        - group: root
        - file_mode: 644
        - dir_mode: 755
        - require:
            - package: nginx
            - file: /etc/nginx/

'/etc/nginx/sites-enabled/default':
    file.absent:
        - require:
            - package: nginx


'/etc/nginx/nginx.conf':
    file.managed:
        - source: salt://nginx/nginx.conf
        - user: root
        - group: root
        - template: jinja
        - mode: 644
        - require:
            - package: nginx

'/etc/nginx/mime.types':
    file.managed:
        - source: salt://nginx/mime.types
        - user: root
        - group: root
        - mode: 644
        - require:
            - package: nginx