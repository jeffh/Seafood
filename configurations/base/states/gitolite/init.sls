{% set user = pillar['gitolite'].get('user', {}) %}
{% set username = user.get('name', 'git') %}
{% set home = user.get('home', '/home/git') }
gitolite:
    pkg:
        - installed
    user.present:
        - name: {{ username }}
        {% if 'uid' in user %}
        - uid: {{ user['uid'] }}
        {% endif %}
        {% if 'gid' in user %}
        - gid: {{ user['gid'] }}
        {% else %}
        - gid_from_name: True
        {% endif %}
        - shell: {{ user.get('shell', '/bin/nologin') }}
        - home: {{ home }}
        - require:
            - group: gitolite
    group.present:
        - name: {{ username }}
        {% if 'gid' in user %}
        - gid: {{ user['gid'] }}
        {% endif %}
    cmd.run:
        - name: '/usr/bin/gl-setup -q {{ home }}/admin.pub'
        - unless: '[ -d "{{ home }}/repositories/gitolite-admin.git" ]'
        - user: {{ username }}
        - group: {{ username }}
        - cwd: {{ home }}
        - require:
            - pkg: gitolite
            - user: gitolite
            - group: gitolite
            - file: '{{ home }}/admin.pub'

'{{ home }}/admin.pub':
    file.managed:
        - source: {{ pillar['gitolite']['admin-key'] }}
        - user: {{ username }}
        - group: {{ username }}
        - mode: 600
        - require:
            - pkg: gitolite
            - user: gitolite
            - group: gitolite
