use_network_time:
    cmd.run:
        - name: 'systemsetup -setusingnetworktime off'
        - onlyif: 'systemsetup -getusingnetworktime | grep -iq ": On"'
