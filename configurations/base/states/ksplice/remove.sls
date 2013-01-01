ksplice:
    pkg.purge:
        - name: uptrack


'/etc/apt/sources.list.d/ksplice.list':
    file.absent:
        - require:
            - pkg: ksplice
    cmd.run:
        - name: 'apt-get update'
        - onlyif: 'apt-cache policy | grep -E ksplice'
        - watch:
            - file: '/etc/apt/sources.list.d/ksplice.list'


'/etc/uptrack/uptrack.conf':
    file.absent:
        - require:
            - pkg: ksplice