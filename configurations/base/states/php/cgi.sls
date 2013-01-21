php-cgi:
    package.installed:
        - name: php5-cgi
        - require:
            - package: nginx
            - user: www-data
            - group: www-data

'/etc/init.d/php-cgi':
    file.managed:
        - source: salt://php/cgi.bash
        - user: root
        - group: root
        - template: jinja
        - defaults:
            pidfile: /var/run/php-fcgi.pid
            phpcgi: /usr/bin/php-cgi
        - require:
            - package: php-cgi

'/etc/monit/conf.d/php-cgi.conf':
    optional_file.managed:
        - onlyif: '[ -e /etc/monit/conf.d/ ]'
        - source: salt://php/cgi.monit
        - user: root
        - group: root
        - template: jinja
        - defaults:
            host: 127.0.0.1
            port: 9000
            user: www-data
            group: www-data
        - require:
            - file: '/etc/init.d/php-cgi'
            - package: php-cgi
