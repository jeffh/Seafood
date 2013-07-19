include:
    - gitolite
    - postfix

{% set user = pillar['gitolite'].get('user', {}) %}
{% set username = user.get('name', 'git') %}
{% set home = user.get('home', '/home/git') %}
'{{ home }}/.gitolite/hooks/common/post-receive':
    file.managed:
        - source: salt://gitolite/files/post-receive/email.hook
        - user: {{ username }}
        - group: {{ username }}
        - mode: 644
        - require:
            - package: gitolite
            - cmd: gitolite-update
            - user: gitolite
            - group: gitolite
