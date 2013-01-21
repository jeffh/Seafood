{% set pg = pillar.get('postgres', {}) %}
{% set version = pg.get('version', '9.1') %}
{% set listen = pg.get('listen', 'localhost') %}
{% set port = pg.get('port', 5432) %}
postgresql:
    package.installed:
        - name: postgresql-{{ version }}
    service.running:
        - enabled: true
        - watch:
            - package: postgresql
            - file: '/etc/postgresql/{{ version }}/main/*'
        - require:
            - user: postgresql
            - group: postgresql
    user.present:
        - name: postgres
        - gid_from_name: True
        - require:
            - group: postgresql
            - package: postgresql
    group.present:
        - name: postgres
        - require:
            - package: postgresql

# monit file
'/etc/monit/conf.d/postgresql.conf':
    optional_file.managed:
        - onlyif: '[ -d "/etc/monit/conf.d/" ]'
        - source: salt://postgresql/monit.conf
        - user: root
        - group: root
        - template: jinja
        - defaults:
            listen: {{ listen }}
            port: {{ port }}
            pidfile: /var/run/postgresql/{{ version }}-main.pid
        - require:
            - package: postgresql

'/etc/postgresql/{{ version }}/main/':
    file.directory:
        - user: root
        - group: root
        - mode: 755
        - require:
            - package: postgresql

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
            listen: {{ listen }}
            port: {{ port }}
            max_connections: {{ pg.get('max_connections', 100) }}
            unix_socket: {{ pg.get('unix_socket', '/var/run/postgresql') }}
            shared_buffers: {{ pg.get('shared_buffers', '24MB') }}
            temp_buffers: {{ pg.get('temp_buffers', '8MB') }}
            work_mem: {{ pg.get('work_mem', '1MB') }}
            maintenance_work_mem: {{ pg.get('maintenance_work_mem', '16MB') }}
            max_files_per_process: {{ pg.get('max_files_per_process', 1000) }}
            effective_cache_size: {{ pg.get('effective_cache_size', '128MB') }}
            checkpoint_segments: {{ pg.get('checkpoint_segments', 3) }}
            checkpoint_completion_target: {{ pg.get("checkpoint_completion_target", '0.5') }}
            max_prepared_transactions: {{ pg.get('max_prepared_transactions', '0') }}
            wal_sync_method: '{{ pg.get("wal_sync_method", "") }}'
            wal_buffers: {{ pg.get('wal_buffers', '-1') }}
            default_statistics_target: {{ pg.get('default_statistics_target', '100') }}
            synchronous_commit: {{ pg.get('synchronous_commit', 'on') }}
            random_page_cost: {{ pg.get('random_page_cost', '4.0') }}
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/pg_ctl.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/pg_ctl.conf
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/start.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/start.conf
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/environment':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/environment
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/pg_hba.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/pg_hba.conf
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'

'/etc/postgresql/{{ version }}/main/pg_ident.conf':
    file.managed:
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - source: salt://postgresql/conf/pg_ident.conf
        - require:
            - file: '/etc/postgresql/{{ version }}/main/'
