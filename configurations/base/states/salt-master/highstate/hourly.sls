'salt-master.highstate.hourly':
    cron.present:
        - name: "cd /opt/saltstack && echo '==============' >> /opt/saltstack/highstate.log && salt '*' state.highstate >> /opt/saltstack/highstate.log"
        - user: root
        - minute: '0'