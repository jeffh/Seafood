{% set version = '9.1' %}
{% set gid = '401' %}

postgresql:
    pkg.installed:
        - name: postgresql-{{ version }}
    service.running:
        - enabled: true
        - watch:
            - pkg: postgresql
            - user: postgresql
            - group: postgresql
    user.present:
        - name: postgres
        - require:
            - group: postgresql
            - pkg: postgresql
    group.present:
        - name: postgres
        - require:
            - pkg: postgresql

# monit file
'/etc/monit/conf.d/postgresql.conf':
    optional_file.managed:
        - onlyif: '[ -d "/etc/monit/conf.d/" ]'
        - source: salt://postgresql/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            listen: localhost
            port: 5432
            pidfile: /var/run/postgresql/{{ version }}-main.pid
        - require:
            - pkg: postgresql

'/etc/postgresql/{{ version }}/main/':
    file.directory:
        - user: root
        - group: root
        - mode: 755
        - require:
            - pkg: postgresql

'/etc/postgresql/{{ version }}/main/postgresql.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/postgresql.conf
# most of these parameters are in:
# http://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
        - defaults:
            version: {{ version }}
            listen: localhost
            port: 5432
            max_connections: 100
            unix_socket: /var/run/postgresql
            shared_buffers: 24MB # min = 128kB
            temp_buffers: 8MB # min = 800kB
            work_mem: 1MB # min = 64kB
            maintenance_work_mem: 16MB
            max_files_per_process: 1000 # min 25
            effective_cache_size: 128MB
            checkpoint_segments: 3
            checkpoint_completion_target: 0.5
            max_prepared_transactions: 0 # 0 = disable
            wal_sync_method: '' # defaults to fdatasync for linux; otherwise fsync
            wal_buffers: -1  # uses default, which is 1/32th of shared_buffers
            default_statistics_target: 100
            synchronous_commit: on
            random_page_cost: 4.0
        - watch_in:
            - service: postgresql
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/pg_ctl.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/pg_ctl.conf
        - watch_in:
            - service: postgresql
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/start.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/start.conf
        - watch_in:
            - service: postgresql
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/environment':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/environment
        - watch_in:
            - service: postgresql
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/pg_hba.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/pg_hba.conf
        - watch_in:
            - service: postgresql
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/pg_ident.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/pg_ident.conf
        - watch_in:
            - service: postgresql
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'
