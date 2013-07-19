sshd:
    package:
        - purged
        - name: openssh-server

'/etc/ssh':
    file:
        - absent

'/etc/monit/conf.d/sshd.conf':
    file:
        - absent
