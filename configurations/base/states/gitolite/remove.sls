{% set user = pillar['gitolite'].get('user', {}) %}
{% set username = user.get('name', 'git') %}
{% set home = user.get('home', '/home/git') }
gitolite:
    pkg:
        - purge
    user.absent:
        - name: {{ username }}
        - require: {{ home }}/admin.pub
    group.absent:
        - name: {{ username }}

{% set files = ['.gitolite', '.gitolite.rc', 'repositories', 'admin.pub']}
{% for file in files %}
'{{ home }}/{{ file }}':
    file:
        - absent
{% endfor %}
