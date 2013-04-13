include:
    - python

virtualenv:
    package.installed:
        - name: python-virtualenv
        - require:
            - package: python