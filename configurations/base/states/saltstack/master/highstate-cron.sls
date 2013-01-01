salt-master-highstate:
    cron.present:
        - name: "cd /opt/saltstack && echo '==============' >> /opt/saltstack/highstate.log && salt '*' state.highstate >> /opt/saltstack/highstate.log"
        - user: root
        {% if minute %}- minute: {{ minute }}{% endif %}
        {% if hour %}- hour: {{ hour }}{% endif %}
        {% if daymonth %}- daymonth: {{ daymonth }}{% endif %}
        {% if month %}- month: {{ month }}{% endif %}
        {% if dayweek %}- dayweek: {{ dayweek }}{% endif %}
