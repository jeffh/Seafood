{% for username in pillar['users'] %}
{% set user = pillar['users'].get(username) %}
{% set username = user.get(username, username) %}
'{{ username }}':
    user.present:
        {% if 'groups' in user %}
        - groups:
            {% for group in user.get('groups', []) %}- {{ group }}
            {% else %}
            []
            {% endfor %}
        {% endif %}
        {% if 'gid' in user %}
        - gid: {{ user['gid'] }}
        {% else %}
        - gid_from_name: True
        {% endif %}
        {% if 'home' in user %}
        - home: {{ user['home'] }}
        {% endif %}
        {% if not user.get('can_login', True) %}
        - shell: /bin/nologin
        {% endif %}
        - require:
            - group: '{{ username }}'
    {% if user.get('pub_key') %}
    ssh_auth.present:
        - user: '{{ username }}'
        - source: '{{ user['pub_key'] }}'
        - require:
            - user: '{{ username }}'
    {% endif %}
    group:
        - present
        {% if 'gid' in user %}
        - gid: {{ user['gid'] }}
        {% endif %}
{% endfor %}
