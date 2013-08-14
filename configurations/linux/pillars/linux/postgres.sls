# most of these parameters are in:
# http://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
#
# All the parameters listed here are optional and have defaults
postgres:
    version: 9.1
    listen: '*'
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
    checkpoint_completion_target: '0.5'
    max_prepared_transactions: '0' # 0 = disable
    wal_sync_method: '' # defaults to fdatasync for linux; otherwise fsync
    wal_buffers: -1  # uses default, which is 1/32th of shared_buffers
    default_statistics_target: 100
    synchronous_commit: on
    random_page_cost: 4.0
    hbas:
        # type  db  user [address] method
        - 'host  all all 127.0.0.1/32 md5'
        - 'host  all all ::1/128      md5'
        - 'host  all all 192.168.0.0/16 md5'
