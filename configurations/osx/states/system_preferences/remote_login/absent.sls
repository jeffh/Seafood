remote_login:
    cmd.run:
        - name: 'systemsetup -setremotelogin -f off'
        - onlyif: "systemsetup -getremotelogin | grep -iq ': On'"
