include:
    - mercurial
    - build-essential

golang:
    package:
        - purged
    cmd.run:
        - name: 'hg clone -u tip https://code.google.com/p/go/ /opt/golang/ && cd /opt/golang/src/ && ./all.bash'
        - require:
            - package: build-essential
            - package: mercurial

