docker:
    cmd.run:
        - name: "sh -x external_files/docker/install.sh"
        - unless: "which dockerd"
