virtualenv:
    pkg.installed:
        - name: python-virtualenv
        - require:
            - pkg: pip