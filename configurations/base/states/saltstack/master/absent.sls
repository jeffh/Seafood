salt-master-highstate:
    cron.absent:
        - name: "cd /opt/saltstack && echo '==============' >> /opt/saltstack/highstate.log && salt '*' state.highstate >> /opt/saltstack/highstate.log"
        - user: root

'/etc/monit/conf.d/salt-master.conf':
    file:
        - absent

'/etc/ufw/applications.d/salt-master':
    file:
        - absent