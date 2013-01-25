elasticsearch:
    cluster_name: elasticsearch
    node_name: {{ grains['fqdn'] }}
    can_be_master: true
    can_store_data: true
    network:
        bind_host: 0.0.0.0
        publish_host: 0.0.0.0
        node_port: 9300
        compress: false
        mlockall: false
    discovery:
        multicast: true
    http:
        enabled: true
        port: 9200
        max_content_length: 100mb
    index:
        number_of_shards: 5
        number_of_replicas: 1
    logging:
        root: 'INFO, console, file'
        action: DEBUG
        com.amazonaws: WARN
        search_slowlog: 'TRACE, index_search_slow_log_file'
        index_slowlog: 'TRACE, index_indexing_slow_log_file'