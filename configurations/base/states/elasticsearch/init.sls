include:
    - java

elasticsearch:
    package:
        - installed
        - require:
            - package: java
    service:
        - running
        - watch:
            - package: elasticsearch
            - file: '/etc/elasticsearch/*'

{% set es = pillar.get('elasticsearch', {}) %}
{% set net = es.get('network', {}) %}
{% set dis = es.get('discovery', {}) %}
{% set http = es.get('http', {}) %}
{% set index = es.get('index', {}) %}
'/etc/elasticsearch/elasticsearch.yml':
    file.managed:
        - source: salt://elasticsearch/elasticsearch.yml
        - user: root
        - group: root
        - template: jinja
        - mode: 640
        - defaults:
            cluster_name: {{ es.get('cluster_name', 'elasticsearch') }}
            node_name: {{ es.get('node_name', grains['fqdn']) }}
            can_be_master: {{ es.get('can_be_master', True) }}
            can_store_data: {{ es.get('can_store_data', True) }}
            mlockall: {{ net.get('mlockall', False) }}
            network:
                bind_host: {{ net.get('bind_host', '0.0.0.0') }}
                publish_host: {{ net.get('publish_host', '0.0.0.0') }}
                node_port: {{ net.get('node_port', 9300) }}
                compress: {{ net.get('compress', False) }}
            discovery:
                multicast: {{ dis.get('multicast', True) }}
            http:
                enabled: {{ http.get('enabled', True) }}
                port: {{ http.get('port', 9200) }}
                max_content_length: {{ http.get('max_content_length', '100mb') }}
            index:
                number_of_shards: {{ index.get('number_of_shards', 5) }}
                number_of_replicas: {{ index.get('number_of_replicas', 1) }}
        - require:
            - package: elasticsearch

{% set log = es.get('logging', {}) %}
'/etc/elasticsearch/logging.yml':
    file.managed:
        - source: salt://elasticsearch/logging.yml
        - user: root
        - group: root
        - template: jinja
        - mode: 640
        - defaults:
            root: "{{ log.get('root', 'INFO, console, file') }}"
            action: "{{ log.get('action', 'DEBUG') }}"
            com_amazonaws: "{{ log.get('com.amazonaws', 'WARN') }}"
            search_slowlog: "{{ log.get('search_slowlog', 'TRACE, index_search_slow_log_file') }}"
            index_slowlog: "{{ log.get('index_slowlog', 'TRACE, index_indexing_slow_log_file')}}"
        - require:
            - package: elasticsearch