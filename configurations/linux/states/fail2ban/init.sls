fail2ban:
    package:
        - installed
    service.running:
        - require:
            - package: fail2ban
        - watch:
            - file: '/etc/fail2ban/*'

'/etc/fail2ban/jail.local':
    file.managed:
        - source: salt://fail2ban/files/jail.local
        - user: root
        - group: root
        - template: jinja
        - mode: 640
        - defaults: 
            find_time: 600
            max_retries: 5
            ban_time: 86400
            email:
                sender: fail2ban@localhost.com
                receiver: jeff@jeffhui.net
            whitelist:
                - 127.0.0.1
                - 172.31.0.0/24
                - 10.10.0.0/24
                - 192.168.0.0/24
        - require:
            - package: fail2ban

