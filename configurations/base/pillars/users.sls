users:
    jeff:
        sudo: true
        gid: 200
        pub_key: salt://users/keys/jeff.pub
        groups:
            - adm
            - cdrom
            - sudo
            - lpadmin
            - sambashare
    rob:
        sudo: true
        gid: 201
        pub_key: salt://users/keys/rob.pub
        groups:
            - adm
            - cdrom
            - sudo
            - lpadmin
            - sambashare