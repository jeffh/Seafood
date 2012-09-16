
iptables:
    pkg:
        - installed

# here, we'll simply defer to a script due to the complexity
# of the iptables config file (one generated by iptables-save)
'/etc/iptables-startup.sh':
    file.managed:
        - source: 'salt://iptables/startup.sh'
        - user: root
        - group: root
        - mode: 755
        - template: jinja
        {% if pillar.get('firewall') %}
        {% set allowed = pillar['firewall'].get('allowed', {}) %}
        {% set default = pillar['firewall'].get('default', {}) %}
        - context:
            allowed_tcp:
                {% for port in allowed.get('tcp', []) %}
                - {{ port }}
                {% else %}
                []
                {% endfor %}
            allowed_udp:
                {% for port in allowed.get('udp', []) %}
                - {{ port }}
                {% else %}
                []
                {% endfor %}
            whitelist:
                {% for ipaddr in pillar['firewall'].get('whitelist', []) %}
                - {{ ipaddr }}
                {% else %}
                []
                {% endfor %}
            blacklist:
                {% for ipaddr in pillar['firewall'].get('blacklist', []) %}
                - {{ ipaddr }}
                {% else %}
                []
                {% endfor %}
            policy:
                input: {{ default.get('input', 'DROP').upper() }}
                forward: {{ default.get('forward', 'DROP').upper() }}
                output: {{ default.get('output', 'ACCEPT').upper() }}
        {% endif %}
        - defaults:
            allowed_tcp: []
            allowed_udp: []
            whitelist: []
            blacklist: []
            root_dir: '/etc/iptables/'
            policy:
                input: drop
                forward: drop
                output: accept
        - require:
            - pkg: iptables

'/etc/iptables-startup.sh && (md5sum /etc/iptables-startup.sh | cut -d " " -f 1 > /tmp/iptables.md5)':
    cmd.run:
        - unless: '[ "`md5sum /etc/iptables-startup.sh | cut -d " " -f 1`" = "`cat /tmp/iptables.md5`" ]'
        - cwd: /
        - shell: /bin/bash
        - watch:
            - pkg: iptables
            - file: /etc/iptables-startup.sh
    crontab.special:
        - require:
            - file: /etc/iptables-startup.sh

'/etc/rsyslog.d/iptables.conf':
    file.managed:
        - source: salt://iptables/iptables.conf
        - require:
            - pkg: iptables
            - file: /etc/rsyslog.d/
        - watch_in:
            - service: syslog