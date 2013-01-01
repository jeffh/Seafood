salt-master:
    pub_port: 4505
    ret_port: 4506
    highstate:
        logfile: /opt/saltstack/highstate.log
        minute: 0
