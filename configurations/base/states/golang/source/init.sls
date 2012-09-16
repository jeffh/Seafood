golang_from_source:
    file.append:
        - name: /etc/environment
        - text: GOROOT=/usr/local/go
    cmd.run:
        - name: 'hg clone -u tip https://code.google.com/p/go && cd go/src && ./all.bash'
        - unless: which go
        - require:
            - pkg: mercurial
            - pkg: git
            - file: golang_from_source