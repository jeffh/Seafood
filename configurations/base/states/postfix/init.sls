postfix:
    pkg:
        - installed
    service.running:
        - watch:
            - pkg: postfix
            - file: '/etc/postfix/*'

{% set files = ['main.cf', 'master.cf', 'dynamicmaps.cf', 'postfix-files', 'postfix-script'] %}

{% for file in files %}
'/etc/postfix/{{ file }}':
    file.managed:
        - source: salt://postfix/files/{{ file }}
        - user: root
        - group: root
        - mode: 600
        - template: jinja
        - defaults:
            system_mail_name: deploy-host
        - require:
            - pkg: postfix
{% endfor %}