ksplice:
    package.installed:
        - name: uptrack
        - require:
            - cmd: '/etc/apt/sources.list.d/ksplice.list'
    cmd.run:
        - name: 'apt-get -yq upgrade kernel kernel-headers kernel-devel; uptrack-upgrade -y'
        - require:
            - file: '/etc/uptrack/uptrack.conf'

'/etc/apt/sources.list.d/ksplice.list':
    file.managed:
        - source: salt://ksplice/source.list
        - user: root
        - group: root
        - mode: 644
        - template: jinja
    cmd.run:
        - name: 'wget -N https://www.ksplice.com/apt/ksplice-archive.asc; apt-key add ksplice-archive.asc; rm -f ksplice-archive.asc; apt-get update'
        - unless: 'apt-cache policy | grep -E ksplice'
        - watch:
            - file: '/etc/apt/sources.list.d/ksplice.list'

'/etc/uptrack/uptrack.conf':
    file.managed:
        - source: salt://ksplice/uptrack.conf
        - user: root
        - group: root
        - mode: 644
        - template: jinja
        - context:
            auto_install: {{ pillar['ksplice']['auto_install']|default('yes') }}
            install_on_reboot: {{ pillar['ksplice']['install_on_reboot']|default('yes') }}
            access_key: {{ pillar['ksplice']['key'] }}
        - require:
            - package: ksplice
