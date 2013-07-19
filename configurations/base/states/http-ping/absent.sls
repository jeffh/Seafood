{% for ping in pillar['http-ping'] %}
ping-{{ ping['name'] }}:
    cron.absent:
        - name: 'curl -k ''{{ ping["url"] }}'' # {{ ping["name"] }}'
        - user: {{ ping.get('user', 'root') }}
{% endfor %}