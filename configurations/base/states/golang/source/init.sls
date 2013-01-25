include:
    - mercurial

golang_from_source:
    environment.set:
        - variables:
            - GOROOT: /usr/local/go
    cmd.run:
        - name: 'cd /usr/local/ && hg clone -u tip https://code.google.com/p/go && cd go/src && ./all.bash'
        - unless: which go
        - require:
            - package: mercurial
            - environment: golang_from_source