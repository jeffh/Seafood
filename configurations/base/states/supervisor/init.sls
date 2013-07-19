include:
    - python.core

supervisor:
	package.installed:
		- order: 1
	service.running:
        - order: last
        - watch:
            - package: supervisor
            - file: /etc/supervisor/supervisord.conf
            - file: /etc/supervisor/config.d/*

'/etc/supervisor/':
    file.recurse:
        - user: root
        - group: root
        - source: salt://supervisor/files
        - clean: True
        - include_empty: True
        - dir_mode: 755
        - file_mode: 644
        - order: 1
        - makedirs: True
        - exclude_pat: '*.template'
        - recurse:
        	- 'conf.d'
        - require:
            - package: supervisor
