'salt-master':
    pub_port: 4505
    ret_port: 4506
    highstate:
        logfile: /opt/saltstack/highstate.log
        # optional
        user: root    # default is root
        minute: '0'   # default is '*'
        hour: '*'     # default is '*'
        daymonth: '*' # default is '*'
        month: '*'    # default is '*'
        dayweek: '*'  # default is '*'
