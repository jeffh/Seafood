use_network_time:
    cmd.run:
        - name: 'systemsetup -setusingnetworktime on'
        - onlyif: 'systemsetup -getusingnetworktime | grep -iq ": Off"'
