# recommended installation is via get.rvm.io... which is a lot messier
ruby-1.9.3:
    pkg.installed:
        - names:
            - build-essential
            - openssl
            - libreadline6
            - libreadline6-dev
            - curl
            - git-core
            - zlib1g
            - zlib1g-dev
            - libssl-dev
            - libyaml-dev
            - libsqlite3-dev
            - sqlite3
            - libxml2-dev
            - libxslt-dev
            - autoconf
            - libc6-dev
            - ncurses-dev
            - automake
            - libtool
            - bison
            - subversion
            - pkg-config
    rvm.installed:
        - default: True
        - require:
            - pkg: ruby-1.9.3