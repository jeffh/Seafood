include:
    - python

pip:
    package.installed:
        - name: python-pip
        - require:
            - package: python