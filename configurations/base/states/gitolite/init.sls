include:
    - git

{% set user = pillar['gitolite'].get('user', {}) %}
{% set username = user.get('name', 'git') %}
{% set home = user.get('home', '/home/git') %}
gitolite:
    package.installed:
        - require:
            - package: git
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
    group.present:
        - name: {{ username }}
        {% if 'gid' in user %}
        - gid: {{ user['gid'] }}
        {% endif %}
        - require:
            - user: gitolite
    cmd.run:
        - name: '/usr/bin/gl-setup -q {{ home }}/admin.pub'
        - unless: '[ -d "{{ home }}/repositories.md5" ]'
        - user: {{ username }}
        - group: {{ username }}
        - cwd: {{ home }}
        - env: "HOME={{ home }}"
        - require:
            - package: gitolite
            - user: gitolite
            - group: gitolite
            - file: '{{ home }}/admin.pub'

gitolite-update:
    cmd.run:
        - name: '/usr/bin/gl-setup -q {{ home }}/admin.pub'
        - unless: '[ "`cat {{ home }}/repositories.md5`" -eq "`find ''{{ home }}/repositories/gitolite-admin.git'' -type f -exec md5sum {} + | awk ''{print $1}'' | sort | md5sum > tee {{ home }}/repositories.md5`" ]'
        - user: {{ username }}
        - group: {{ username }}
        - cwd: {{ home }}
        - env: "HOME={{ home }}"
        - require:
            - package: gitolite
            - user: gitolite
            - group: gitolite
            - file: '{{ home }}/admin.pub'
        - watch:
            - file: '{{ home }}/repositories'


'{{ home }}/.gitolite.rc':
    file.managed:
        - source: salt://gitolite/gitolite.rc
        - user: {{ username }}
        - group: {{ username }}
        - mode: 644
        - require:
            - package: gitolite
            - cmd: gitolite
            - user: gitolite
            - group: gitolite

'{{ home }}/repositories':
    file.directory:
        - user: {{ username }}
        - group: {{ username }}
        - file_mode: 600
        - dir_mode: 700
        - require:
            - package: gitolite


'{{ home }}/admin.pub':
    file.managed:
        - source: {{ pillar['gitolite']['admin-key'] }}
        - user: {{ username }}
        - group: {{ username }}
        - mode: 600
        - require:
            - package: gitolite
            - user: gitolite
            - group: gitolite
