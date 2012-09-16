nginx:
    pkg:
        - installed
    service.running:
        - watch:
            - pkg: nginx
            - file: '/etc/nginx/*'

'/etc/monit/conf.d/nginx.conf':
    optional_file.managed:
        - ifonly: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://nginx/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            http_port: 80
            https_port: 443
            pidfile: /var/run/nginx.pid

'/usr/share/nginx/www/':
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - pkg: nginx
            
'/etc/nginx/sites-available':
    file:
        - absent
        - require:
            - pkg: nginx
            
'/etc/nginx/':
    file.directory:
        - user: root
        - group: root
        - file_mode: 755
        - require:
            - pkg: nginx
            
'/etc/nginx/sites-enabled/':
    file.recurse:
        - user: root
        - group: root
        - mode: 644
        - clean: true
        - source: salt://nginx/sites/
        - require:
            - pkg: nginx
            - file: /etc/nginx/
            

'/etc/nginx/nginx.conf':
    file.managed:
        - source: salt://nginx/nginx.conf
        - user: root
        - group: root
        - template: jinja
        - mode: 644
        - require:
            - pkg: nginx

'/etc/nginx/mime.types':
    file.managed:
        - source: salt://nginx/mime.types
        - user: root
        - group: root
        - mode: 644
        - require:
            - pkg: nginx