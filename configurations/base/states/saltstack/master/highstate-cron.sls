{% set master = pillar['salt-master']['highstate'] %}
{% set keys = ['minute', 'hour', 'daymonth', 'month', 'dayweek'] %}
salt-master-highstate:
    cron.present:
        - name: "cd /opt/saltstack && echo '==============' >> /opt/saltstack/highstate.log && salt '*' state.highstate >> /opt/saltstack/highstate.log"
        - user: {{ ping.get('user', 'root') }}
        {% for key in keys %}
        {% if key in ping %}- {{ key }}: {{ ping[key] }}{% endif %}
        {% endfor %}
