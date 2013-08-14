remote_login:
    cmd.run:
        - name: 'systemsetup -setremotelogin on'
        - onlyif: "systemsetup -getremotelogin | grep -iq ': Off'"
