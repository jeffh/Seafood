users:
    pi:
        sudo: true
        gid: 1000
        pub_key: salt://users/keys/jeff.pub
        groups:
            - adm
            - dialout
            - cdrom
            - sudo
            - audio
            - video
            - plugdev
            - games
            - users
            - input