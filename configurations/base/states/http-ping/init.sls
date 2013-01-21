include:
    - tools.curl

{% set keys = ['minute', 'hour', 'daymonth', 'month', 'dayweek'] %}
{% for ping in pillar['http-ping'] %}
"ping-{{ ping['name'] }}":
    cron.present:
        - name: 'curl -k ''{{ ping["url"] }}'' # {{ ping["name"] }}'
        - user: {{ ping.get('user', 'root') }}
        {% for key in keys %}
        {% if key in ping %}- {{ key }}: '{{ ping[key] }}'{% endif %}
        {% endfor %}
        - require:
            - package: curl
{% endfor %}