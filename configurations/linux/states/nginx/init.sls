nginx:
    package:
        - installed
    service.running:
        - watch:
            - package: nginx
            - file: '/etc/nginx/*'
    user.present:
        - name: www-data
        - gid_from_name: True
        - require:
            - group: nginx
    group.present:
        - name: www-data


'/etc/monit/conf.d/nginx.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://monit/files/conf.d/basic.conf.template
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - template: jinja
        - defaults:
            name: {{ salt['pillar.get']('pillar:nginx:service_name', 'nginx') }}
            pidfile: /var/run/nginx.pid

'/usr/share/nginx/www/':
    file.directory:
        - user: www-data
        - group: www-data
        - mode: 755
        - require:
            - user: www-data
            - group: www-data
            - package: nginx

'/etc/nginx/sites-available':
    file:
        - absent
        - require:
            - package: nginx

'/etc/nginx/':
    file.directory:
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - file_mode: 755
        - require:
            - package: nginx

'/etc/nginx/sites-enabled/':
    file.directory:
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
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
        - source: salt://nginx/files/nginx.conf
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - template: jinja
        - mode: 644
        - require:
            - package: nginx

'/etc/nginx/mime.types':
    file.managed:
        - source: salt://nginx/files/mime.types
        - user: {{ salt['pillar.get']('root:user', 'root') }}
        - group: {{ salt['pillar.get']('root:group', 'root') }}
        - mode: 644
        - require:
            - package: nginx
