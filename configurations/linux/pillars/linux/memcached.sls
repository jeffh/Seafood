memcached:
    user: memcache
    port: 11211
    memory: 64
    max_value_size: 8M
    listen: 127.0.0.1
    max_connections: 1024
    error_on_max: false
    verbose: false
    logfile: /var/log/memcached.log