{% set user = pillar['gitolite'].get('user', {}) %}
{% set username = user.get('name', 'git') %}
{% set home = user.get('home', '/home/git') %}
gitolite:
    package:
        - purged
    user.absent:
        - name: {{ username }}
        - require:
            - file: {{ home }}/admin.pub
    group.absent:
        - name: {{ username }}

{% set files = ['.gitolite', '.gitolite.rc', 'repositories', 'admin.pub'] %}
{% for file in files %}
'{{ home }}/{{ file }}':
    file:
        - absent
{% endfor %}
