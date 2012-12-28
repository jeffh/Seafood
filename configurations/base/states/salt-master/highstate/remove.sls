'salt-master.highstate.hourly':
    crontab.absent:
        - name: "cd /opt/saltstack && echo '==============' >> /opt/saltstack/highstate.log && salt '*' state.highstate >> /opt/saltstack/highstate.log"
        - user: root

