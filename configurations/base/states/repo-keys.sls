{% set p = pillar.get('repo-keys', {}) %}
{% set key_dir = p.get('cache-dir', '/opt/salt/repo_keys_cache/') %}
repo_keys:
    file.directory:
        - name: {{ key_dir }}
        - user: root
        - group: root
        - mode: 755
        - order: 10

{% for name, data in p.get('add-keys', {}).items() %}
'{{ key_dir }}/{{ name }}':
    file.managed:
        - source: {{ data['source'] }}
        {% if 'source_hash' in data %}
        - source_hash: {{ data['source_hash'] }}
        {% endif %}
        - require:
            - file: repo_keys
        - order: 10
    cmd.run:
        - name: 'apt-key add {{ key_dir }}/{{ name }}'
        - unless: 'apt-key list | grep -q "/{{ data['id'] }} "'
        - require:
            - file: '{{ key_dir }}/{{ name }}'
        - order: 10
{% endfor %}

{% for name, data in p.get('remove-keys', {}).items() %}
'{{ key_dir }}/{{ name }}':
    file.purged:
        - require:
            - file: repo_keys
        - order: 10
    cmd.run:
        - name: 'apt-key add {{ key_dir }}/{{ name }}'
        - onlyif: 'apt-key list | grep -q "/{{ data['id'] }} "'
        - require:
            - file: '{{ key_dir }}/{{ name }}'
        - order: 10
{% endfor %}

