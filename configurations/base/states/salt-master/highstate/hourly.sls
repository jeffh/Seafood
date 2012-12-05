'salt-master.highstate.hourly':
    cron.set_special:
        - user: root
        - special: @hourly
        - cmd: "cd /opt/saltstack && echo '==============' >> /opt/saltstack/highstate.log && salt '*' state.highstate >> /opt/saltstack/highstate.log"