remote_desktop:
    cmd.run:
        - name: '/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -off'
        - onlyif: "ps aux | grep -iq 'ARDAgent$'"

