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
