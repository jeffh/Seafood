firewall:
    allowed:
        tcp:
            - 22  # ssh
            - 25  # postfix (receive mail)
            - 80  # http
            - 443 # https
            - 465 # postfix (encrypted send)
            - 587 # postfix (send)
            {% if salt['cmd.has_exec']('salt-master') %}
            - 4505
            - 4506
            {% endif %}
