firewall:
    allowed:
        tcp:
            - 22  # ssh
            - 80  # http
            - 443 # https
            {% if salt['cmd.has_exec']('salt-master') %}
            - 4505
            - 4506
            {% endif %}
