include:
    - mercurial

golang_from_source:
    environment.set:
        - variables:
            - GOOS: linux
            - GOARCH: arm
            - GOROOT: /usr/local/go
    cmd.run:
        - name: 'cat /etc/environment | while read $var; do export $var; done && hg clone -u tip https://code.google.com/p/go && cd go/src && ./all.bash'
        - unless: which go
        - require:
            - package: mercurial
            - file: golang_from_source
