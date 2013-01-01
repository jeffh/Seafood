ufw:
    pkg.purge:
        - require:
            cmd: ufw
    service.dead:
        - enabled: false
        - require:
            cmd: ufw
    cmd.run:
        - name: 'ufw disable'
        - onlyif: 'ufw status | grep -E " active"'
