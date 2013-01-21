include:
    - python
    - python.dev

virtualenv:
    package.installed:
        - name: python-virtualenv
        - require:
            - package: python