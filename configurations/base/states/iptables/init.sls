iptables:
    package:
        - installed
    iptables.managed:
        - name: '/etc/iptables.rules'
        - policies:
            INPUT: DROP
            OUTPUT: DROP
            FORWARD: DROP
        - rules:
            - 'INPUT -j LOGDROP'
            - 'OUTPUT -j LOGDROP'
            - 'FORWARD -j LOGDROP'
        - allow_existing: true
        - protocols:
            - ping
            - dns
            - ssh
            - http
            - https
        - incoming:
            - destination_port: 80
              protocol: tcp
            - destination_port: 443
              protocol: tcp
        - require:
            - package: iptables

'/etc/network/if-up.d/iptables':
    file.managed:
        - source: salt://iptables/files/startup.sh
        - user: root
        - group: root
        - template: jinja
        - mode: 751
        - defaults:
            rules: '/etc/iptables.rules'
        - require:
            - package: iptables
            - iptables: iptables

