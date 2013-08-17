remote_desktop:
    cmd.run:
        - name: '/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -on -restart -agent -privs -all -allowAccessFor -allUsers'
        #- unless: "ps aux | grep -iq 'ARDAgent$'"
